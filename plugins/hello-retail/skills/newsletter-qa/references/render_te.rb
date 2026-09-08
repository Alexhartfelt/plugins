#!/usr/bin/env ruby
# Local preview renderer for Hello Retail Triggered Email templates (newsletter-qa, lane T).
# There is no MCP render tool for Triggered Emails, so this resolves base + content block with
# sample products and writes plain HTML you can screenshot with Playwright (file://…).
#
# Usage: PATH=$HOME/.rbenv/shims:$PATH LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
#        ruby render_te.rb <base.liquid> <content.liquid> <samples.json> <out.html> [include_voucher=true|false]
#
# samples.json shape: see samples.example.json next to this file. "currency" sets the
# priceWithCurrency suffix; prices are formatted 1.234,56 (swap the separators in HrFilters
# for a shop that uses 1,234.56 — the point is a stable preview, not the website's exact format).
#
# Known harness limits (NOT findings against the design): Ruby Liquid rejects parentheses inside
# {% if %} conditions, which HR's engine accepts — rewrite the condition locally and rerun.
#
# HR-specific syntax handled here before handing the rest to Ruby Liquid:
#   {# type name = "default" #}   -> parsed into the render context, then stripped
#   {% block name %}...{% endblock %} -> extracted and injected into {{ blocks.name }}
#   | price                       -> Danish number format (1.234,56)
#   | priceWithCurrency           -> "1.234,56 <currency>" (currency from samples.json, default DKK)
Encoding.default_external = Encoding::UTF_8
Encoding.default_internal = Encoding::UTF_8
require "liquid"
require "json"

base_path, content_path, samples_path, out_path, voucher = ARGV
abort "usage: render_te.rb base.liquid content.liquid samples.json out.html [true|false]" unless out_path

module HrFilters
  def price(v)
    n = v.to_f
    int, dec = ("%.2f" % n).split(".")
    int = int.reverse.scan(/\d{1,3}/).join(".").reverse
    "#{int},#{dec}"
  end

  def priceWithCurrency(v, currency = nil)
    "#{price(v)} #{currency || $hr_currency}"
  end
end
Liquid::Template.register_filter(HrFilters)

def parse_params(src)
  params = {}
  src.scan(/\{#\s*(text|color|number|font|boolean|multiline)\s+([a-zA-Z0-9_]+)\s*=\s*"((?:[^"\\]|\\.)*)"\s*#\}/) do |type, name, val|
    params[name] = case type
                   when "boolean" then val == "true"
                   else val
                   end
  end
  params
end

def strip_params(src)
  src.gsub(/\{#\s*(text|color|number|font|boolean|multiline)\s+[a-zA-Z0-9_]+\s*=\s*"(?:[^"\\]|\\.)*"\s*#\}\s*\n?/, "")
end

def extract_block(src, name)
  m = src.match(/\{%\s*block\s+#{name}\s*%\}(.*?)\{%\s*endblock\s*%\}/m)
  m ? m[1] : ""
end

base_src = File.read(base_path, encoding: "UTF-8")
content_src = File.read(content_path, encoding: "UTF-8")
samples = JSON.parse(File.read(samples_path, encoding: "UTF-8"))
$hr_currency = samples["currency"] || "DKK"

params = parse_params(base_src).merge(parse_params(content_src))
params["include_voucher"] = (voucher == "true") if voucher

ctx = params.merge(
  "products" => samples["products"],
  "relatedProducts" => samples["relatedProducts"],
  "cart_url" => samples["cart_url"],
  "cart_total" => samples["cart_total"],
  "unsubscribe_url" => "https://example.invalid/unsubscribe",
  "subject" => params["title"]
)

content_body = strip_params(content_src)
blocks = {}
%w[preheader content].each do |b|
  tpl = Liquid::Template.parse(extract_block(content_body, b), error_mode: :lax)
  blocks[b] = tpl.render(ctx, strict_variables: false)
  warn "[#{b}] liquid errors: #{tpl.errors.map(&:message).join(' | ')}" unless tpl.errors.empty?
end

base_tpl = Liquid::Template.parse(strip_params(base_src), error_mode: :lax)
html = base_tpl.render(ctx.merge("blocks" => blocks), strict_variables: false)
warn "[base] liquid errors: #{base_tpl.errors.map(&:message).join(' | ')}" unless base_tpl.errors.empty?

File.write(out_path, html)
puts "wrote #{out_path} (#{html.bytesize} bytes)"

# frozen_string_literal: true

require "strscan"

# Inline TeX as plain Unicode text, for the places that cannot run MathJax: a page's meta
# description, which search results and link previews show as it is. `$X\times Y$` becomes
# "X × Y", `$f\colon V\to W$` "f: V → W", `$x_1,\dots,x_k$` "x₁, …, xₖ".
#
# The conversion is deliberately small. Anything it cannot write faithfully as text — a
# fraction of fractions, a subscript with no Unicode form such as `0_V`, an environment, a
# macro of the site's own — makes `convert` return nil, and the caller leaves that math out
# rather than show a reader `\whitestar` or a wrong formula.
module ExternalTexText
  class Unsupported < StandardError; end

  Atom = Struct.new(:text, :kind)

  GREEK = {
    "alpha" => "α", "beta" => "β", "gamma" => "γ", "delta" => "δ", "epsilon" => "ϵ",
    "varepsilon" => "ε", "zeta" => "ζ", "eta" => "η", "theta" => "θ", "vartheta" => "ϑ",
    "iota" => "ι", "kappa" => "κ", "lambda" => "λ", "mu" => "μ", "nu" => "ν", "xi" => "ξ",
    "pi" => "π", "varpi" => "ϖ", "rho" => "ρ", "varrho" => "ϱ", "sigma" => "σ",
    "varsigma" => "ς", "tau" => "τ", "upsilon" => "υ", "phi" => "ϕ", "varphi" => "φ",
    "chi" => "χ", "psi" => "ψ", "omega" => "ω", "Gamma" => "Γ", "Delta" => "Δ",
    "Theta" => "Θ", "Lambda" => "Λ", "Xi" => "Ξ", "Pi" => "Π", "Sigma" => "Σ",
    "Upsilon" => "Υ", "Phi" => "Φ", "Psi" => "Ψ", "Omega" => "Ω"
  }.freeze

  ORDINARY = {
    "infty" => "∞", "emptyset" => "∅", "varnothing" => "∅", "forall" => "∀", "exists" => "∃",
    "nexists" => "∄", "neg" => "¬", "lnot" => "¬", "partial" => "∂", "nabla" => "∇",
    "ell" => "ℓ", "aleph" => "ℵ", "hbar" => "ℏ", "wp" => "℘", "Re" => "ℜ", "Im" => "ℑ",
    "top" => "⊤", "bot" => "⊥", "angle" => "∠", "prime" => "′", "dots" => "…",
    "ldots" => "…", "cdots" => "⋯", "vdots" => "⋮", "ddots" => "⋱", "square" => "□",
    "Box" => "□", "blacksquare" => "■", "dagger" => "†", "ddagger" => "‡", "S" => "§",
    "P" => "¶", "vert" => "|", "lvert" => "|", "rvert" => "|", "Vert" => "‖", "lVert" => "‖",
    "rVert" => "‖", "|" => "‖", "#" => "#", "%" => "%", "&" => "&", "$" => "$", "_" => "_",
    "triangle" => "△", "natural" => "♮", "flat" => "♭", "sharp" => "♯"
  }.freeze

  RELATIONS = {
    "in" => "∈", "notin" => "∉", "ni" => "∋", "subset" => "⊂", "subseteq" => "⊆",
    "subsetneq" => "⊊", "supset" => "⊃", "supseteq" => "⊇", "supsetneq" => "⊋",
    "le" => "≤", "leq" => "≤", "ge" => "≥", "geq" => "≥", "ne" => "≠", "neq" => "≠",
    "lt" => "<", "gt" => ">", "equiv" => "≡", "sim" => "∼", "simeq" => "≃", "cong" => "≅",
    "approx" => "≈", "propto" => "∝", "to" => "→", "rightarrow" => "→", "leftarrow" => "←",
    "gets" => "←", "mapsto" => "↦", "longrightarrow" => "⟶", "longmapsto" => "⟼",
    "hookrightarrow" => "↪", "twoheadrightarrow" => "↠", "Rightarrow" => "⇒",
    "implies" => "⇒", "Leftarrow" => "⇐", "impliedby" => "⇐", "Leftrightarrow" => "⇔",
    "iff" => "⇔", "leftrightarrow" => "↔", "Longrightarrow" => "⟹",
    "Longleftrightarrow" => "⟺", "uparrow" => "↑", "downarrow" => "↓", "mid" => "∣",
    "nmid" => "∤", "parallel" => "∥", "perp" => "⊥", "prec" => "≺", "succ" => "≻",
    "preceq" => "⪯", "succeq" => "⪰", "ll" => "≪", "gg" => "≫", "models" => "⊨",
    "vdash" => "⊢", "dashv" => "⊣", "coloneqq" => "≔", "sqsubseteq" => "⊑",
    "sqsupseteq" => "⊒", "trianglelefteq" => "⊴", "triangleleft" => "◁"
  }.freeze

  BINARY = {
    "times" => "×", "cdot" => "·", "circ" => "∘", "cap" => "∩", "cup" => "∪",
    "setminus" => "∖", "smallsetminus" => "∖", "pm" => "±", "mp" => "∓", "oplus" => "⊕",
    "otimes" => "⊗", "wedge" => "∧", "land" => "∧", "vee" => "∨", "lor" => "∨", "ast" => "∗",
    "star" => "⋆", "div" => "÷", "bullet" => "•", "sqcup" => "⊔", "sqcap" => "⊓",
    "amalg" => "⨿"
  }.freeze

  LARGE_OPERATORS = {
    "sum" => "∑", "prod" => "∏", "coprod" => "∐", "bigcup" => "⋃", "bigcap" => "⋂",
    "bigoplus" => "⨁", "bigotimes" => "⨂", "bigvee" => "⋁", "bigwedge" => "⋀",
    "bigsqcup" => "⨆", "int" => "∫", "iint" => "∬", "oint" => "∮"
  }.freeze

  NAMED_OPERATORS = %w[
    lim sup inf max min det dim ker deg gcd lg ln log exp sin cos tan sec csc cot sinh cosh
    tanh arcsin arccos arctan arg hom Pr mod
  ].to_h { |name| [name, name] }.merge(
    "bmod" => "mod", "liminf" => "lim inf", "limsup" => "lim sup"
  ).freeze

  OPENING = { "{" => "{", "lbrace" => "{", "langle" => "⟨", "lfloor" => "⌊", "lceil" => "⌈" }.freeze
  CLOSING = { "}" => "}", "rbrace" => "}", "rangle" => "⟩", "rfloor" => "⌋", "rceil" => "⌉" }.freeze

  SPACES = [",", ":", ";", ">", " ", "quad", "qquad", "enspace", "thinspace", "medspace",
            "thickspace"].freeze
  IGNORED = %w[
    ! left right middle big Big bigg Bigg bigl bigr Bigl Bigr biggl biggr Biggl Biggr
    displaystyle textstyle scriptstyle scriptscriptstyle limits nolimits mathstrut strut
    allowbreak nonumber notag
  ].freeze

  NEGATED = {
    "∈" => "∉", "=" => "≠", "⊆" => "⊈", "⊂" => "⊄", "⊇" => "⊉", "⊃" => "⊅", "∣" => "∤",
    "≡" => "≢", "∼" => "≁", "≅" => "≇", "≈" => "≉", "<" => "≮", ">" => "≯", "≤" => "≰",
    "≥" => "≱"
  }.freeze

  PLAIN_FONTS = %w[mathbf boldsymbol bm mathit mathrm mathsf mathtt mathnormal].freeze
  TEXT_COMMANDS = %w[text textrm textit textbf textsf texttt textnormal mbox hbox].freeze
  ACCENTS = {
    "overline" => "\u0305", "bar" => "\u0304", "widebar" => "\u0305", "hat" => "\u0302",
    "widehat" => "\u0302", "tilde" => "\u0303", "widetilde" => "\u0303", "dot" => "\u0307",
    "ddot" => "\u0308", "vec" => "\u20D7", "underline" => "\u0332"
  }.freeze

  SUPERSCRIPTS = {
    "0" => "⁰", "1" => "¹", "2" => "²", "3" => "³", "4" => "⁴", "5" => "⁵", "6" => "⁶",
    "7" => "⁷", "8" => "⁸", "9" => "⁹", "+" => "⁺", "-" => "⁻", "−" => "⁻", "=" => "⁼",
    "(" => "⁽", ")" => "⁾", "a" => "ᵃ", "b" => "ᵇ", "c" => "ᶜ", "d" => "ᵈ", "e" => "ᵉ",
    "f" => "ᶠ", "g" => "ᵍ", "h" => "ʰ", "i" => "ⁱ", "j" => "ʲ", "k" => "ᵏ", "l" => "ˡ",
    "m" => "ᵐ", "n" => "ⁿ", "o" => "ᵒ", "p" => "ᵖ", "r" => "ʳ", "s" => "ˢ", "t" => "ᵗ",
    "u" => "ᵘ", "v" => "ᵛ", "w" => "ʷ", "x" => "ˣ", "y" => "ʸ", "z" => "ᶻ", "A" => "ᴬ",
    "B" => "ᴮ", "D" => "ᴰ", "E" => "ᴱ", "G" => "ᴳ", "H" => "ᴴ", "I" => "ᴵ", "J" => "ᴶ",
    "K" => "ᴷ", "L" => "ᴸ", "M" => "ᴹ", "N" => "ᴺ", "O" => "ᴼ", "P" => "ᴾ", "R" => "ᴿ",
    "T" => "ᵀ", "U" => "ᵁ", "V" => "ⱽ", "W" => "ᵂ", "′" => "′", "∗" => "*", "*" => "*",
    "∘" => "°"
  }.freeze

  SUBSCRIPTS = {
    "0" => "₀", "1" => "₁", "2" => "₂", "3" => "₃", "4" => "₄", "5" => "₅", "6" => "₆",
    "7" => "₇", "8" => "₈", "9" => "₉", "+" => "₊", "-" => "₋", "−" => "₋", "=" => "₌",
    "(" => "₍", ")" => "₎", "a" => "ₐ", "e" => "ₑ", "h" => "ₕ", "i" => "ᵢ", "j" => "ⱼ",
    "k" => "ₖ", "l" => "ₗ", "m" => "ₘ", "n" => "ₙ", "o" => "ₒ", "p" => "ₚ", "r" => "ᵣ",
    "s" => "ₛ", "t" => "ₜ", "u" => "ᵤ", "v" => "ᵥ", "x" => "ₓ", "β" => "ᵦ", "γ" => "ᵧ",
    "ρ" => "ᵨ", "φ" => "ᵩ", "χ" => "ᵪ", "," => ","
  }.freeze

  # Mathematical alphanumerics: the letters Unicode placed in the Letterlike Symbols block
  # before it had the rest, then the offset of the rest in the Mathematical block.
  DOUBLE_STRUCK = {
    "holes" => { "C" => "ℂ", "H" => "ℍ", "N" => "ℕ", "P" => "ℙ", "Q" => "ℚ", "R" => "ℝ", "Z" => "ℤ" },
    "upper" => 0x1D538, "lower" => 0x1D552, "digit" => 0x1D7D8
  }.freeze
  SCRIPT = {
    "holes" => { "B" => "ℬ", "E" => "ℰ", "F" => "ℱ", "H" => "ℋ", "I" => "ℐ", "L" => "ℒ",
                 "M" => "ℳ", "R" => "ℛ", "e" => "ℯ", "g" => "ℊ", "o" => "ℴ" },
    "upper" => 0x1D49C, "lower" => 0x1D4B6
  }.freeze
  FRAKTUR = {
    "holes" => { "C" => "ℭ", "H" => "ℌ", "I" => "ℑ", "R" => "ℜ", "Z" => "ℨ" },
    "upper" => 0x1D504, "lower" => 0x1D51E
  }.freeze
  ALPHABETS = {
    "mathbb" => DOUBLE_STRUCK, "Bbb" => DOUBLE_STRUCK, "mathcal" => SCRIPT,
    "mathscr" => SCRIPT, "mathfrak" => FRAKTUR
  }.freeze

  module_function

  # The math as text, or nil when it cannot be written faithfully.
  def convert(tex)
    atoms = Parser.new(tokenize(tex.to_s)).parse
    text = join(atoms)
    text.empty? ? nil : text
  rescue Unsupported
    nil
  end

  def tokenize(tex)
    scanner = StringScanner.new(tex)
    tokens = []

    until scanner.eos?
      if scanner.scan(/\\([A-Za-z]+)\*?/)
        tokens << [:command, scanner[1]]
      elsif scanner.scan(/\\(.)/m)
        tokens << [:command, scanner[1]]
      elsif scanner.scan(/\s+/)
        tokens << [:space, " "]
      elsif scanner.scan(/[{}^_&~']/)
        tokens << [:special, scanner.matched]
      else
        tokens << [:char, scanner.getch]
      end
    end

    tokens
  end

  # TeX's spacing, approximated with plain spaces: none between ordinary symbols, a space on
  # each side of a relation or a binary operation, one after a comma, none inside brackets.
  def join(atoms)
    atoms = classify_unary(atoms.reject { |atom| atom.kind == :space && atom.text.empty? })
    output = +""
    previous = nil

    atoms.each do |atom|
      if atom.kind == :space
        output << " "
        next
      end

      output << gap(previous, atom)
      output << atom.text
      previous = atom
    end

    output.gsub(/ {2,}/, " ").strip
  end

  # A binary operation with nothing on its left is a sign: −1, +∞.
  def classify_unary(atoms)
    previous = nil
    atoms.map do |atom|
      next atom if atom.kind == :space

      if atom.kind == :bin && (previous.nil? || %i[rel bin open punct colon op].include?(previous.kind))
        atom = Atom.new(atom.text, :ord)
      end
      previous = atom
      atom
    end
  end

  def gap(left, right)
    return "" if left.nil?
    return "" if %i[close punct colon].include?(right.kind)
    return "" if left.kind == :open
    return " " if %i[rel bin punct colon].include?(left.kind) || %i[rel bin].include?(right.kind)
    return (right.kind == :open ? "" : " ") if left.kind == :op
    return " " if right.kind == :op && %i[ord close].include?(left.kind)

    ""
  end

  def tight(atoms)
    atoms.reject { |atom| atom.kind == :space }.map(&:text).join
  end

  def alphabet_letter(alphabet, char)
    return alphabet["holes"][char] if alphabet["holes"].key?(char)
    return [alphabet["upper"] + char.ord - "A".ord].pack("U") if char.match?(/\A[A-Z]\z/)
    return [alphabet["lower"] + char.ord - "a".ord].pack("U") if char.match?(/\A[a-z]\z/)
    return [alphabet["digit"] + char.to_i].pack("U") if alphabet["digit"] && char.match?(/\A\d\z/)

    raise Unsupported
  end

  def script(text, table)
    text.each_char.map { |char| table.fetch(char) { raise Unsupported } }.join
  end

  class Parser
    def initialize(tokens)
      @tokens = tokens
      @index = 0
    end

    def parse
      atoms = []
      until @index >= @tokens.length
        raise Unsupported if peek == [:special, "}"]

        atoms.concat(atom_with_scripts)
      end
      atoms
    end

    private

    def peek
      @tokens[@index]
    end

    def advance
      token = @tokens[@index]
      @index += 1
      token
    end

    def skip_spaces
      @index += 1 while peek && peek[0] == :space
    end

    # A braced group, or else the next single atom: what `\mathbb R` or `x^2` takes.
    def argument
      skip_spaces
      raise Unsupported unless peek

      if peek == [:special, "{"]
        group
      else
        token = peek
        raise Unsupported if token[0] == :special && token[1] != "'"

        atom
      end
    end

    def group
      advance # {
      atoms = []
      until peek == [:special, "}"]
        raise Unsupported unless peek

        atoms.concat(atom_with_scripts)
      end
      advance # }
      atoms
    end

    # The characters of an argument as written, for \text and the alphabets: a braced run of
    # letters, digits and spaces, or one character.
    def raw_argument
      skip_spaces
      raise Unsupported unless peek
      return [advance[1]] if peek[0] == :char
      raise Unsupported unless peek == [:special, "{"]

      advance
      chars = []
      depth = 0
      loop do
        kind, value = advance
        raise Unsupported unless kind

        case [kind, value]
        in [:special, "{"] then depth += 1
        in [:special, "}"]
          break if depth.zero?

          depth -= 1
        in [:special, "~"] | [:space, _] | [:command, " " | "," | ";" | ":"] then chars << " "
        in [:command, "!"] then nil
        in [:special, "'"] then chars << "’"
        in [:char, _] then chars << value
        else raise Unsupported
        end
      end
      chars
    end

    def atom_with_scripts
      skip_spaces
      return [] unless peek

      if script_follows?
        base = [Atom.new("", :ord)]
      else
        base = atom
        return base if base.empty? && !script_follows?

        base = [Atom.new("", :ord)] if base.empty?
      end
      loop do
        skip_spaces
        token = peek
        if token == [:special, "'"]
          advance
          base[-1] = Atom.new(base[-1].text + "′", base[-1].kind)
        elsif token == [:special, "^"] || token == [:special, "_"]
          advance
          table = token[1] == "^" ? SUPERSCRIPTS : SUBSCRIPTS
          text = ExternalTexText.script(ExternalTexText.tight(argument), table)
          base[-1] = Atom.new(base[-1].text + text, base[-1].kind)
        else
          break
        end
      end
      base
    end

    def script_follows?
      skip_spaces
      [[:special, "^"], [:special, "_"]].include?(peek)
    end

    def atom
      token = advance
      kind, value = token

      case kind
      when :space
        []
      when :char
        [char_atom(value)]
      when :special
        special_atom(value)
      when :command
        command_atom(value)
      end
    end

    def char_atom(char)
      case char
      when "+" then Atom.new("+", :bin)
      when "-" then Atom.new("−", :bin)
      when "*" then Atom.new("∗", :bin)
      when "=", "<", ">", ":" then Atom.new(char, :rel)
      when ",", ";" then Atom.new(char, :punct)
      when "(", "[" then Atom.new(char, :open)
      when ")", "]" then Atom.new(char, :close)
      else Atom.new(char, :ord)
      end
    end

    def special_atom(value)
      case value
      when "{"
        @index -= 1
        group
      when "~" then [Atom.new(" ", :space)]
      when "'" then [Atom.new("′", :ord)]
      else raise Unsupported # }, ^ and _ out of place, & of an alignment
      end
    end

    def command_atom(name)
      return [Atom.new(GREEK[name], :ord)] if GREEK.key?(name)
      return [Atom.new(RELATIONS[name], :rel)] if RELATIONS.key?(name)
      return [Atom.new(BINARY[name], :bin)] if BINARY.key?(name)
      return [Atom.new(ORDINARY[name], :ord)] if ORDINARY.key?(name)
      return [Atom.new(LARGE_OPERATORS[name], :op)] if LARGE_OPERATORS.key?(name)
      return [Atom.new(NAMED_OPERATORS[name], :op)] if NAMED_OPERATORS.key?(name)
      return [Atom.new(OPENING[name], :open)] if OPENING.key?(name)
      return [Atom.new(CLOSING[name], :close)] if CLOSING.key?(name)
      return [Atom.new(" ", :space)] if SPACES.include?(name)
      return ignored(name) if IGNORED.include?(name)
      return [Atom.new(":", :colon)] if name == "colon"
      return alphabet(name) if ALPHABETS.key?(name)
      return [Atom.new(ExternalTexText.tight(argument), :ord)] if PLAIN_FONTS.include?(name)
      return [Atom.new(raw_argument.join.strip, :op)] if name == "operatorname"
      return [Atom.new(raw_argument.join, :ord)] if TEXT_COMMANDS.include?(name)
      return accent(name) if ACCENTS.key?(name)
      return fraction if %w[frac dfrac tfrac].include?(name)
      return root if name == "sqrt"
      return negation if name == "not"
      return modulus if name == "pmod"

      raise Unsupported
    end

    def ignored(name)
      # \left. and \right. open or close nothing.
      @index += 1 if %w[left right].include?(name) && peek == [:char, "."]
      []
    end

    def alphabet(name)
      letters = raw_argument.reject { |char| char == " " }
      raise Unsupported if letters.empty?

      text = letters.map { |char| ExternalTexText.alphabet_letter(ALPHABETS[name], char) }.join
      [Atom.new(text, :ord)]
    end

    def accent(name)
      text = ExternalTexText.tight(argument)
      raise Unsupported unless text.grapheme_clusters.length == 1

      [Atom.new(text + ACCENTS[name], :ord)]
    end

    def fraction
      numerator = ExternalTexText.join(argument)
      denominator = ExternalTexText.join(argument)
      raise Unsupported if numerator.empty? || denominator.empty?

      [Atom.new("#{parenthesized(numerator)}/#{parenthesized(denominator)}", :ord)]
    end

    def root
      raise Unsupported if peek == [:char, "["]

      [Atom.new("√#{parenthesized(ExternalTexText.join(argument))}", :ord)]
    end

    # A number, or one letter with its primes and scripts, needs no parentheses: 1/x, 1/(2y).
    def parenthesized(text)
      text.match?(/\A(?:\p{N}+|\p{L}[\p{Lm}\p{No}′]*)\z/) ? text : "(#{text})"
    end

    def negation
      skip_spaces
      following = atom
      raise Unsupported unless following.length == 1 && following[0].kind == :rel

      relation = following[0].text
      [Atom.new(NEGATED.fetch(relation) { relation + "\u0338" }, :rel)]
    end

    def modulus
      [Atom.new(" ", :space), Atom.new("(mod #{ExternalTexText.join(argument)})", :ord)]
    end
  end
end

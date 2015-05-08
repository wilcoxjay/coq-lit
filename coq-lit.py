import sys
import re

def tangle(lines):
    pass


sep = ["\n", " ", ".", ",", "(", ")", ":", "=", ";", "\"", "+", "-", "*", "{", "}", "[", "]"]

binder_skip = ["\n", " ", ".", "(", ")", ";", "\"", "+", "-", "*", ">", "{", "}"]

def tokenize(line):
    global sep
    last = 0
    i = 0

    while i < len(line):
        if line[i] in sep:
            if i > last:
                yield line[last:i]
            yield line[i]
            last = i+1
        i += 1
    if last < len(line):
        yield line[last:]

def highlight(line):
    global sep
    vernacular_color = "a020f0"
    syntax_color = "228b22"
    no_fail_tactic_color = "00008b"
    fail_tactic_color = "ff0000"
    global_bound_color = "3b10ff"
    local_bound_color = "a0522d"

    vernacular_binder = [
        "Definition",
        "Inductive",
        "Fixpoint",
        "Theorem",
        "Lemma",
        "Example",
        "Ltac",
        "Record",
        "Variable",
        "Section",
        "End",
        "Instance",
        "Module",
        "Context"
    ]
    vernacular_words = vernacular_binder + [
        "Proof",
        "Qed",
        "Defined",
        "Require",
        "Import",
        "Print",
        "Assumptions",

    ]

    local_binder = [
        "forall",
        "fun"
    ]

    syntax_words = local_binder + [
        "Type",
        "Set",
        "Prop",
        "if",
        "then",
        "else",
        "match",
        "with",
        "end",
        "as",
        "in",
        "return",
        "using",
        "let"
    ]
    no_fail_tactic_words = [
        "auto",
        "destruct",
        "exists",
        "split",
        "intros",
        "unfold",
        "inversion",
        "refine",
        "rewrite",
        "subst",
        "simpl",
        "apply",
        "dependent",
        "destruction",
        "firstorder",
        "intuition",
        "eauto",
        "pattern",
        "clear",
        "induction",
        "fold",
        "erewrite",
        "revert",
        "eexists",
        "eapply",
        "exfalso",
        "compute"
    ]
    fail_tactic_words = [
        "reflexivity",
        "by",
        "discriminate",
        "congruence",
        "solve"
    ]
    tactical_words = [
        "try",
        "repeat"
    ]


    def style_template(color, word):
        return "<span style='color:#" + color + "'>" + word + "</span>"

    def is_tactical(word):
        return word in tactical_words

    def is_vernacular(word):
        return word in vernacular_words

    def is_syntax(word):
        return word in syntax_words

    def is_no_fail_tactic(word):
        return word in no_fail_tactic_words

    def is_fail_tactic(word):
        return word in fail_tactic_words

    def is_vernac_binder(word):
        return word in vernacular_binder

    def is_local_binder(word):
        return word in local_binder

    def color_word(word):
        if is_vernacular(word):
            return style_template(vernacular_color, word)
        elif is_syntax(word):
            return style_template(syntax_color, word)
        elif is_no_fail_tactic(word):
            return style_template(no_fail_tactic_color, word)
        elif is_fail_tactic(word):
            return style_template(fail_tactic_color, word)
        elif is_tactical(word):
            return style_template(vernacular_color, word)
        else:
            return word

    words = list(tokenize(line))
    #print(words, file=sys.stderr)
    output = [word for word in words]
    i = 0
    while i < len(words):
        word = words[i]
        output[i] = color_word(word)
        if is_vernac_binder(word):
            j = i+1
            while j < len(words) and words[j] in sep:
                j += 1
            if j < len(words):
                output[j] = style_template(global_bound_color, words[j])
            i = j
        if is_local_binder(word):
            j = i+1
            while j < len(words):
                while j < len(words) and words[j] in binder_skip:
                    j += 1
                if j < len(words) and words[j] in [",", ":", "="]:
                    break
                if j < len(words):
                    output[j] = style_template(local_bound_color, words[j])
                    j += 1
            i = j
        i += 1

    return output

def escape(s):
    assert type(s) == type("")
    out = []
    for c in s:
        if c == "\\":
            out += "\\\\"
        elif c == "\n":
            out += "\\n"
        elif c == "\"":
            out += "\\\""
        else:
            out += c
    return "".join(out)

def unicodify(s):
    assert type(s) == type("")
    replacements = {
        #"->": "→",
        #"/\\": "∧"
    }
    for src, dst in replacements.items():
        print(src, dst, file=sys.stderr)
        s = s.replace(src, dst)
    return s


def weave(lines):
    MARKDOWN = 1
    CODE = 2
    SKIP = 3
    RAW = 4
    CONTEXT = 5
    USE_CONTEXT = 6

    current_context = 0

    state = [SKIP]

    def end_use_context():
        print("</span>", end='')
        state.pop()

    i = 0
    while i < len(lines):
        line = lines[i]
        #print(state, line, file=sys.stderr, end='')

        if line.startswith("(**"):
            state.append(MARKDOWN)
        elif line.startswith("*)") and state[-1] != CODE:
            if state[-1] == CONTEXT:
                #print("leaving context", file=sys.stderr)
                print("</code></pre>\",\n            open: function (event, ui) {\n                ui.tooltip.css('max-width', 'none');\n                ui.tooltip.css('min-width', '800px');\n            }\n        });\n});\n</script>", end='')
                state[-1] = USE_CONTEXT
                print("<span title='tooltip' id='context-" + str(current_context-1) + "'>", end='')
            else:
                state.pop()
        elif line.startswith("(*begin code"):
            state.append(CODE)
            print("<pre><code>", end='')
        elif line.startswith("(*end code") or line.startswith("end code*)"):
            #print(state[-1], file=sys.stderr)
            assert state[-1] == CODE
            state.pop()
            print("</code></pre>", end='')
        elif line.startswith("(*raw"):
            state.append(RAW)
        elif line.startswith("(*context"):
            if state[-1] == USE_CONTEXT:
                end_use_context()
            state.append(CONTEXT)
            #print("entering context", file=sys.stderr)
            print("<script>\n$(function () {\n    $(\"#context-" + str(current_context) +
                  "\").tooltip({\n            content: \"<pre><code>", end='')
            current_context += 1
        elif line.startswith("(*") and state[-1] != CODE:
            state.append(state[-1])

        else:
            if re.match(r"\s*\*\)", line):
                print("WARNING: line contains closing comment with only whitespace preceding it on line. possible syntax error\n", line, file=sys.stderr)
            if state[-1] != SKIP:
                if state[-1] == CODE or state[-1] == USE_CONTEXT:
                    out = "".join(highlight(line))
                    out = unicodify(out)
                    print("    ", out, end='', sep='')
                    if state[-1] == USE_CONTEXT:
                        end_use_context()
                elif state[-1] == CONTEXT:
                    out = "".join(highlight(line))
                    out = escape(unicodify(out))
                    print(out, end='')
                else:
                    print(line, end='')
        i += 1


def usage():
    pass

if __name__ == '__main__':
    options = [arg[1:] for arg in sys.argv[1:] if arg.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    if len(args) < 1:
        print("Need filename on commandline.")
        usage()
        sys.exit(1)

    filename = args[0]

    with open(filename) as f:
        lines = list(f)
        if "tangle" in options:
            tangle(lines)
        elif "weave" in options:
            weave(lines)
        else:
            print("You didn't tell me tangle or weave.")
            usage()
            sys.exit(1)

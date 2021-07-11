"""
    domonic.d3.format
    ==================================

"""

from domonic.javascript import Math, Array, Number, String, Global, RegExp

# import {formatDecimalParts} from "./formatDecimal.js";


def formatDecimal(x):
    x = Math.round(x)
    if Math.abs(x) >= 1e21:
        return x.toLocaleString("en").replace(r'/,/g', "")
    else:
        return x.toString(10)


def formatDecimalParts(x, p):
    """[ Computes the decimal coefficient and exponent of the specified number x with
        significant digits p, where x is positive and p is in [1, 21] or undefined.
        For example, formatDecimalParts(1.23) returns ["123", 0].]

    Args:
        x ([type]): [description]
        p ([type]): [description]

    Returns:
        [type]: [description]
    """
    p = x.toExponential(p - 1) if p else x.toExponential()
    x = p.indexOf("e")
    i = x
    if i < 0:
        return None  # NaN, ±Infinity

    # i = None
    coefficient = x.slice(0, i)

    # The string returned by toExponential either has the form \d\.\d+e[-+]\d+
    # (e.g., 1.2e+3) or the form \de[-+]\d+ (e.g., 1e+3).
    return [
        coefficient[0] + coefficient.slice(2) if coefficient.length > 1 else coefficient,
        x.slice(i + 1)
    ]

# --- formatPrefixAuto
# import formatPrefixAuto from "./formatPrefixAuto.js";


prefixExponent = None


def formatPrefixAuto(x, p):
    d = formatDecimalParts(x, p)
    if not d:
        return x + ""

    coefficient = d[0]
    exponent = d[1]
    prefixExponent = Math.max(-8, Math.min(8, Math.floor(exponent / 3)))
    i = exponent - (prefixExponent * 3) + 1
    n = coefficient.length

    if i == n:
        return coefficient
    else:
        if i > n:
            return coefficient + Array(i - n + 1).join("0")
        else:
            if i > 0:
                return coefficient.slice(0, i) + "." + coefficient.slice(i)
            else:
                return "0." + Array(1 - i).join("0") + formatDecimalParts(x, Math.max(0, p + i - 1))[0]


# formatRounded
# import formatRounded from "./formatRounded.js";


def formatRounded(x, p):
    d = formatDecimalParts(x, p)
    if not d:
        return x + ""
    coefficient = d[0]
    exponent = d[1]
    if exponent < 0:
        return "0." + Array(-exponent).join("0") + coefficient
    else:
        if (coefficient.length > exponent + 1):
            return coefficient.slice(0, exponent + 1) + "." + coefficient.slice(exponent + 1)
        else:
            return coefficient + Array(exponent - coefficient.length + 2).join("0")


formatTypes = {
            "%": lambda x, p: (x * 100).toFixed(p),
            "b": lambda x: Math.round(x).toString(2),
            "c": lambda x: x + "",
            "d": formatDecimal,
            "e": lambda x, p: x.toExponential(p),
            "f": lambda x, p: x.toFixed(p),
            "g": lambda x, p: x.toPrecision(p),
            "o": lambda x: Math.round(x).toString(8),
            "p": lambda x, p: formatRounded(x * 100, p),
            "r": formatRounded,
            "s": formatPrefixAuto,
            "X": lambda x: Math.round(x).toString(16).toUpperCase(),
            "x": lambda x: Math.round(x).toString(16)
        }


# import exponent from "./exponent.js";


def exponent(x):
    x = formatDecimalParts(Math.abs(x))
    return x[1] if x else None


# import formatGroup from ".['formatGroup'].js";

def formatGroup(grouping, thousands):
    def func(value, width):
        i = value.length
        t = []
        j = 0
        g = grouping[0]
        length = 0

        while (i > 0 and g > 0):
            if (length + g + 1 > width):
                g = Math.max(1, width - length)

            a = i - g
            b = i + g
            t.append(value.substring(a, b))

            alen = length + g + 1
            if (alen > width):
                break

            j = (j + 1)
            g = grouping[j % grouping.length]

        return t.reverse().join(thousands)

    return func


# import formatNumerals from "./formatNumerals.js";


def formatNumerals(numerals):
    def func(value):
        return value.replace(r'/[0-9]/g', lambda i: numerals[i])
    return func


# import formatSpecifier from "./formatSpecifier.js";


# [[fill]align][sign][symbol][0][width][,][.precision][~][type]
re = r'^(?:(.)?([<>=^]))?([+\-( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?(~)?([a-z%])?$'


def formatSpecifier(specifier):
    # print('spec:', specifier)
    match = RegExp(re).exec(specifier)
    print(match)
    if not match:
        raise Exception("invalid format: " + specifier)

    # match = None
    return FormatSpecifier({
                'fill': match[0], 'align': match[1],
                'sign': match[2], 'symbol': match[3],
                'zero': match[4], 'width': match[5],
                'comma': match[6],
                'precision': match[7] and String(match[7]).slice(1),
                'trim': match[8],
                'type': match[9]
                })


class FormatSpecifier():

    def __init__(self, specifier):
        self.fill = " " if specifier.get('fill', None) == None else specifier.fill + ""
        self.align = ">" if specifier.get('align', None) == None else specifier.align + ""
        self.sign = "-" if specifier.get('sign', None) == None else specifier.sign + ""
        self.symbol = "" if specifier.get('symbol', None) == None else specifier.symbol + ""
        self.zero = bool(specifier.get('zero', False))
        self.width = None if specifier.get('width', None) == None else specifier.get('width')
        self.comma = bool(specifier.get('comma', None))
        self.precision = None if specifier.get('precision', None) == None else specifier.get('precision')
        self.trim =  bool(specifier.get('trim', None))
        self.type = "" if specifier.get('type', None) == None else specifier.get('type') + ""

    def toString(self):
        return self.fill + self.align + self.sign + self.symbol + "0" if self.zero else "" + \
            "" if self.width == None else Math.max(1, self.width | 0) + "," if self.comma else "" + \
            "" if self.precision == None else "." + Math.max(0, self.precision | 0) + \
            "~" if self.trim else "" + self.type


# import formatTrim from "./formatTrim.js";

# // Trims insignificant zeros, e.g., replaces 1.2000k with 1.2k.
def formatTrim(s):
    #   out:
    #   for (var n = s.length, i = 1, i0 = -1, i1; i < n; ++i) {

    n = s.length
    i = 1
    i0 = -1
    i1 = None

#   for (var n = s.length, i = 1, i0 = -1, i1; i < n; ++i) {

    for i in range(1, n):
        if s[i] == ".":
            i0 = i1 = i
            break
        elif s[i] == "0":
            if i0 == 0:
                i0 = i
                i1 = i
                break
        else:
            if not s[i]:
                break  # out
            if (i0 > 0):
                i0 = 0
                break

    return s.slice(0, i0) + s.slice(i1 + 1) if i0 > 0 else s


# import identity from "./identity.js";


def identity(x):
    return x  # ? huh


# import exponent from "./exponent.js";
# import formatGroup from "./formatGroup.js";
# import formatNumerals from "./formatNumerals.js";
# import formatSpecifier from "./formatSpecifier.js";
# import formatTrim from "./formatTrim.js";
# import formatTypes from "./formatTypes.js";
# import {prefixExponent} from "./formatPrefixAuto.js";

# .src/locale.js

map = Array.map
prefixes = ["y", "z", "a", "f", "p", "n", "µ", "m", "", "k", "M", "G", "T", "P", "E", "Z", "Y"]


class formatLocale():

    def __init__(self, locale):

        self.group = locale['grouping'] == None or identity if locale['thousands'] == None else formatGroup(locale['grouping'], locale['thousands'] + "")
        self.currencyPrefix = "" if locale['currency'] == None else locale['currency'][0] + ""
        self.currencySuffix = "" if locale['currency'] == None else locale['currency'][1] + ""
        self.decimal = "." if locale.get('decimal', None) == None else locale['decimal'] + ""
        self.numerals = identity if locale.get('numerals', None) == None else formatNumerals(locale['numerals'])
        self.percent = "%" if locale.get('percent', None) == None else locale['percent'] + ""
        self.minus = "−" if locale.get('minus', None) == None else locale['minus'] + ""
        self.nan = "NaN" if locale.get('nan', None) == None else locale['nan'] + ""

    def newFormat(self, specifier):
        specifier = formatSpecifier(specifier)

        fill = specifier.fill
        align = specifier.align
        sign = specifier.sign
        symbol = specifier.symbol
        zero = specifier.zero
        width = specifier.width
        comma = specifier.comma
        precision = specifier.precision
        trim = specifier.trim
        type = specifier.type

        # The "n" type is an alias for ",g".
        if type == "n":
            comma = True
            type = "g"

        # The "" type, and any invalid type, is an alias for ".12~g".
        elif not formatTypes[type]:
            if precision == None:
                precision = 12
                trim = True
                type = "g"

        # If zero fill is specified, padding goes after sign and before digits.
        if (zero or (fill == "0" and align == "=")):
            zero = True
            fill = "0"
            align = "="

        # Compute the prefix and suffix.
        # For SI-prefix, the suffix is lazily computed.
        prefix = ""
        if symbol == "$":
            prefix = self.currencyPrefix
        else:
            if (symbol == "#" and String('/[boxX]/').test(type)):
                prefix = "0" + type.toLowerCase()
            else:
                prefix = ""

        suffix = ""
        if symbol == "$":
            suffix = self.currencySuffix
        else:
            suffix = self.percent if RegExp(r'/[%p]/').test(type) else ""

        # What format function should we use?
        # Is this an integer type?
        # Can this type generate exponential notation?
        formatType = formatTypes[type]
        maybeSuffix = RegExp(r'/[defgprs%]/').test(type)

        # Set the default precision if not specified,
        # or clamp the specified precision to the supported range.
        # For significant precision, it must be in [1, 21].
        # For fixed precision, it must be in [0, 20].
        if precision == None:
            precision = 6
        else:
            precision = Math.max(1, Math.min(21, precision)) if RegExp(r'/[gprs]/').test(type) else Math.max(0, Math.min(20, precision))

        def format(value):
            valuePrefix = prefix
            valueSuffix = suffix
            i = None
            n = None
            c = None

            if (type == "c"):
                valueSuffix = formatType(value) + valueSuffix
                value = ""
            else:
                value = value

                # Determine the sign. -0 is not less than 0, but 1 / -0 is!
                valueNegative = value < 0 or 1 / value < 0

                # Perform the initial formatting.
                value = self.nan if Global.isNaN(value) else formatType(Math.abs(value), precision)

                # Trim insignificant zeros.
                if trim:
                    value = formatTrim(value)

                # If a negative value rounds to zero after formatting, and no explicit positive sign is requested, hide the sign.
                if (valueNegative and value == 0 and sign != "+"):
                    valueNegative = False

                # Compute the prefix and suffix.
                # valuePrefix = (valueNegative ? (sign == "(" ? sign : minus) : sign == "-" or sign == "(" ? "" : sign) + valuePrefix
                a = sign if sign == "(" else self.minus
                b = "" if sign == "(" else sign
                valuePrefix = (a if valueNegative else sign == "-" or b) + valuePrefix

                valueSuffix = (prefixes[8 + prefixExponent / 3] if type == "s" else "") + valueSuffix + (")" if valueNegative and sign == "(" else "")

                # Break the formatted value into the integer “value” part that can be
                # grouped, and fractional or exponential “suffix” part that is not.
                if maybeSuffix:
                    i = -1
                    n = value.length
                while i < n:
                    c = value.charCodeAt(i)
                    if 48 > c or c > 57:
                        valueSuffix = self.decimal + value.slice(i + 1) if c == 46 else value.slice(i) + valueSuffix
                        value = value.slice(0, i)
                        break
                    i += 1

            # If the fill character is not "0", grouping is applied before padding.
            if comma and not zero:
                value = self.group(value, Global.Infinity)

            # Compute the padding.
            length = valuePrefix.length + value.length + valueSuffix.length
            padding = Array(width - length + 1).join(fill) if length < width else ""

            # If the fill character is "0", grouping is applied after padding.
            if comma and zero:
                value = self.group(padding + value, width - valueSuffix.length if padding.length else Global.Infinity)
                padding = ""

            # Reconstruct the final output based on the desired alignment.

            if align == "<":
                value = valuePrefix + value + valueSuffix + padding
            elif align == "=":
                value = valuePrefix + padding + value + valueSuffix
            elif align == "^":
                length = padding.length >> 1
                value = padding.slice(0, length) + valuePrefix + value + valueSuffix + padding.slice(length)
            else:
                value = padding + valuePrefix + value + valueSuffix

            return self.numerals(value)

            # format.toString = function() {
            # return specifier + "";
            # };
            # return format

    def formatPrefix(self, specifier, value):
        specifier = formatSpecifier(specifier)
        specifier.type = "f"
        f = self.newFormat(specifier)
        e = Math.max(-8, Math.min(8, Math.floor(exponent(value) / 3))) * 3
        k = Math.pow(10, -e)
        prefix = prefixes[8 + e / 3]
        return lambda value: f(k * value) + prefix

    format = newFormat

    # def __repr__(self):
        # return {"format": self.newFormat, "formatPrefix": self.formatPrefix}

    # return {
    #     format: newFormat,
    #     formatPrefix: formatPrefix
    # };
    # }


locale = None
format = None
formatPrefix = None


def defaultLocale(definition):
    global locale
    global format
    global formatPrefix
    locale = formatLocale(definition)
    print('AAA:',locale.format)
    format = locale.format
    formatPrefix = locale.formatPrefix  # ['formatPrefix']
    return locale



defaultLocale({'thousands': ",", "grouping": [3], "currency": ["$", ""]})

# formatDefaultLocale, 
# format, 
# formatPrefix}
# precisionFixed
# precisionPrefix
# precisionRound
# def format( number_string ):
    # return 
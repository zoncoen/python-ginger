#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple grammar checker

This grammar checker will fix grammar mistakes using Ginger.
"""

import sys
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
import json


class ColoredText:
    """Colored text class"""
    colors = ['black', 'red', 'green', 'orange', 'blue', 'magenta', 'cyan', 'white']
    color_dict = {}
    for i, c in enumerate(colors):
        color_dict[c] = (i + 30, i + 40)

    @classmethod
    def colorize(cls, text, color=None, bgcolor=None):
        """Colorize text
        @param cls Class
        @param text Text
        @param color Text color
        @param bgcolor Background color
        """
        c = None
        bg = None
        gap = 0
        if color is not None:
            try:
                c = cls.color_dict[color][0]
            except KeyError:
                print("Invalid text color:", color)
                return(text, gap)

        if bgcolor is not None:
            try:
                bg = cls.color_dict[bgcolor][1]
            except KeyError:
                print("Invalid background color:", bgcolor)
                return(text, gap)

        s_open, s_close = '', ''
        if c is not None:
            s_open = '\033[%dm' % c
            gap = len(s_open)
        if bg is not None:
            s_open += '\033[%dm' % bg
            gap = len(s_open)
        if not c is None or bg is None:
            s_close = '\033[0m'
            gap += len(s_close)
        return('%s%s%s' % (s_open, text, s_close), gap)


def get_ginger_url(text):
    """Get URL for checking grammar using Ginger.
    @param text English text
    @return URL
    """
    API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"

    scheme = "http"
    netloc = "services.gingersoftware.com"
    path = "/Ginger/correct/json/GingerTheText"
    params = ""
    query = urllib.parse.urlencode([
        ("lang", "US"),
        ("clientVersion", "2.0"),
        ("apiKey", API_KEY),
        ("text", text)])
    fragment = ""

    return(urllib.parse.urlunparse((scheme, netloc, path, params, query, fragment)))


def get_ginger_result(text):
    """Get a result of checking grammar.
    @param text English text
    @return result of grammar check by Ginger
    """
    url = get_ginger_url(text)

    try:
        response = urllib.request.urlopen(url)
    except HTTPError as e:
            print("HTTP Error:", e.code)
            quit()
    except URLError as e:
            print("URL Error:", e.reason)
            quit()

    try:
        result = json.loads(response.read().decode('utf-8'))
    except ValueError:
        print("Value Error: Invalid server response.")
        quit()

    return(result)


def main():
    """main function"""
    original_text = " ".join(sys.argv[1:])
    if len(original_text) > 600:
        print("You can't check more than 600 characters at a time.")
        quit()
    fixed_text = original_text
    results = get_ginger_result(original_text)

    # Correct grammar
    if(not results["LightGingerTheTextResult"]):
        print("Good English :)")
        quit()

    # Incorrect grammar
    color_gap, fixed_gap = 0, 0
    for result in results["LightGingerTheTextResult"]:
        if(result["Suggestions"]):
            from_index = result["From"] + color_gap
            to_index = result["To"] + 1 + color_gap
            suggest = result["Suggestions"][0]["Text"]

            # Colorize text
            colored_incorrect = ColoredText.colorize(original_text[from_index:to_index], 'red')[0]
            colored_suggest, gap = ColoredText.colorize(suggest, 'green')

            original_text = original_text[:from_index] + colored_incorrect + original_text[to_index:]
            fixed_text = fixed_text[:from_index-fixed_gap] + colored_suggest + fixed_text[to_index-fixed_gap:]

            color_gap += gap
            fixed_gap += to_index-from_index-len(suggest)

    print("from: " + original_text)
    print("to:   " + fixed_text)


if __name__ == '__main__':
    main()

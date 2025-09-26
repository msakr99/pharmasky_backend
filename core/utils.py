def get_excel_header(tab_name="Report", header_title="Report"):
    return {
        "tab_title": tab_name,
        "use_header": True,
        "header_title": header_title,
        "style": {
            "alignment": {
                "horizontal": "center",
                "vertical": "center",
                "wrapText": True,
                "shrink_to_fit": True,
            },
            "font": {
                "name": "Arial",
                "size": 16,
                "bold": True,
                "color": "FF000000",
            },
        },
    }


def get_excel_column_header(titles=[]):
    return {
        "titles": titles,
        "height": 25,
        "style": {
            "fill": {
                "fill_type": "solid",
                "start_color": "cccccc",
            },
            "alignment": {
                "horizontal": "center",
                "vertical": "center",
                "wrapText": True,
                "shrink_to_fit": True,
            },
            "border_side": {
                "border_style": "thin",
                "color": "FF000000",
            },
            "font": {
                "name": "Arial",
                "size": 12,
                "color": "FF000000",
            },
        },
    }


def get_excel_body():
    return {
        "style": {
            "alignment": {
                "horizontal": "center",
                "vertical": "center",
                "wrapText": True,
                "shrink_to_fit": True,
            },
        },
        "height": 40,
    }

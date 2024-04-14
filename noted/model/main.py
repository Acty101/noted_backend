import noted
import google.generativeai as genai
import json


def predict_audio(filepath, audio_prompt, model):
    prompt = audio_prompt
    audio_file = genai.upload_file(path=filepath)
    response = model.generate_content([prompt, audio_file])
    return convert_string_data(response.text)


import json


def convert_string_data(data):
    """Converts string data with delimiters into a structured format.

    Args:
      data: The input string containing delimited sections.

    Returns:
      A list of dictionaries representing the converted data.
    """

    def process_paragraph(text):
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": text},
                    }
                ]
            },
        }

    def process_bulleted_list(text):
        items = []
        for line in text.strip().split("\n"):
            if line.startswith("- "):
                items.append(
                    {
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": line[2:].strip()},
                                }
                            ]
                        },
                    }
                )
        return items

    def process_math(text):
        return {
            "object": "block",
            "type": "equation",
            "equation": {"expression": text.strip()},
        }

    parts = []
    current_part = []
    current_delimiter = None

    for line in data.splitlines():
        line = line.strip()
        if line.startswith("|||") or line.startswith("~~~") or line.startswith("###"):
            if current_delimiter:
                # Process previous part
                content = "\n".join(current_part)
                if current_delimiter == "|||":
                    parts.append(process_paragraph(content))
                elif current_delimiter == "~~~":
                    parts.extend(process_bulleted_list(content))
                elif current_delimiter == "###":
                    parts.append(process_math(content))
            current_part = []  # Reset for the next part
            current_delimiter = line[:3]
        else:
            current_part.append(line)

    # Process last part (if any and not empty)
    if current_delimiter and current_part:
        content = "\n".join(current_part)
        if current_delimiter == "|||":
            parts.append(process_paragraph(content))
        elif current_delimiter == "~~~":
            parts.extend(process_bulleted_list(content))
        elif current_delimiter == "###":
            parts.append(process_math(content))

    return parts


def main():
    # Example usage:
    input_data = """
    |||
    This is a paragraph.
    It can have multiple lines.
    |||
    ~~~
    - First item
    - Second item
    ~~~
    ###
    E=mc^2
    ###
    """

    converted_data = convert_string_data(input_data)
    print(json.dumps(converted_data, indent=2))


if __name__ == "__main__":
    main()

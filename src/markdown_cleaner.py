


def clean_markdown(text: str) -> str:
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        stripped = line.strip()
        if stripped == "":
            cleaned.append("\n\n")
            continue
        if stripped == "\n":
            cleaned.append("\n\n")
            continue
        
        # if len(stripped) < 20:
        #     continue

        cleaned.append(stripped)

    return "\n".join(cleaned)

if __name__ == "__main__":
    # from crawler import scrape
    # markdown= scrape(["https://docs.langchain.com/oss/python/integrations/tools"])[0]['content']
    # cleaned_markdown= clean_markdown(markdown)
    # print(cleaned_markdown)
    print('This code works for now.')
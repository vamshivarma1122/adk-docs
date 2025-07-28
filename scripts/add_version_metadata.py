import os
import re

def add_version_metadata(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                with open(filepath, "r+") as f:
                    content = f.read()
                    # Remove the old, incorrect version line if it exists
                    content = re.sub(r"^version: 1.0\n", "", content)

                    if content.startswith("---"):
                        # Front matter exists, add version if it's not there
                        if "version:" not in content.split("---")[1]:
                            parts = content.split("---")
                            front_matter = parts[1]
                            body = "---".join(parts[2:])
                            new_front_matter = front_matter + "version: 1.0\n"
                            content = "---" + new_front_matter + "---" + body
                    else:
                        # No front matter, create a new one
                        content = "---\nversion: 1.0\n---\n\n" + content

                    f.seek(0)
                    f.write(content)
                    f.truncate()

if __name__ == "__main__":
    add_version_metadata("docs/")
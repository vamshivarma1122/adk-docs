import os
import re
from collections import defaultdict

def generate_version_report(directory):
    version_map = defaultdict(list)
    files_without_version = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.read()
                    if content.startswith("---"):
                        front_matter = content.split("---")[1]
                        match = re.search(r"version:\s*(.*)", front_matter)
                        if match:
                            version = match.group(1).strip()
                            version_map[version].append(filepath)
                        else:
                            files_without_version.append(filepath)
                    else:
                        files_without_version.append(filepath)

    # --- Generate the new report content ---
    report_content = "<!-- BEGIN_VERSION_REPORT -->\n"
    report_content += "# Documentation Version Report\n\n"
    report_content += "This report provides a summary of the versions of the documentation pages.\n\n"

    for version, files in sorted(version_map.items()):
        report_content += f"## Version {version}\n\n"
        report_content += f"Found {len(files)} pages with this version:\n\n"
        for file in files:
            link = os.path.relpath(file, "docs").replace(".md", ".html")
            report_content += f"- [{file}]({link})\n"
        report_content += "\n"

    if files_without_version:
        report_content += "## Pages without Version Information\n\n"
        report_content += f"Found {len(files_without_version)} pages without version metadata:\n\n"
        for file in files_without_version:
            link = os.path.relpath(file, "docs").replace(".md", ".html")
            report_content += f"- [{file}]({link})\n"
        report_content += "\n"
    report_content += "<!-- END_VERSION_REPORT -->"

    # --- Read the existing report and replace the version section ---
    report_path = "docs_health_report.md"
    try:
        with open(report_path, "r") as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = ""

    # Use a regex to replace the content between the markers, or append if not found
    # The re.DOTALL flag allows "." to match newlines
    pattern = re.compile(r"<!-- BEGIN_VERSION_REPORT -->.*<!-- END_VERSION_REPORT -->", re.DOTALL)
    
    if pattern.search(existing_content):
        new_full_content = pattern.sub(report_content, existing_content)
    else:
        # If the markers aren't found, append the new report with a newline
        new_full_content = existing_content + "\n\n" + report_content

    with open(report_path, "w") as f:
        f.write(new_full_content)

    print(f"\nSuccessfully updated version report in {report_path}")

if __name__ == "__main__":
    generate_version_report("docs/")

import os
import shutil
import markdown

import generate
from sources import SOURCES


def main() -> None:
    # refresh RSS feeds
    generate.main()

    with open('README.md', 'r') as f:
        base_index_md = f.read()

    base_index_md += """
## Custom RSS Feeds

"""
    for source in SOURCES:
        base_index_md += f"- {source.title} - [RSS](./feeds/{source.output_filename}) - [Source]({source.link})\n"

    if os.path.exists('html'):
        shutil.rmtree('html')
    os.makedirs('html')
    # copy feeds/ to html/ folder
    shutil.copytree('feeds', 'html/feeds')
    with open('html/index.html', 'w') as f:
        f.write(markdown.markdown(base_index_md))

if __name__ == '__main__':
    main()
    
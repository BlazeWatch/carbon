from bs4 import BeautifulSoup
import shutil
import pathlib
import logging
import streamlit as st


def add_custom_scripts():
    id = "ZAKAR_CUSTOM_SCRIPT"
    custom_js = f"""
    <script type="module" async>
        let script = document.createElement('script');
        script.setAttribute('type', 'module');
        script.setAttribute('id', '{id}');
        const text = await fetch("/app/static/script.js").then(r=>r.text());
        script.textContent = text;
        document.head.appendChild(script);
    </script>
    """

    # Identify html path of streamlit
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if id not in index_path.read_text():  # if id not found within html file
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # backup recovery
        else:
            shutil.copy(index_path, bck_index)  # save backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + custom_js)
        index_path.write_text(new_html)  # insert analytics tag at top of head

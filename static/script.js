setInterval(() => {
    document.body.querySelector("footer").innerText = "Made with suffering, and ofcourse streamlit"
}, 1000)


function checkForScripts(node) {
    document.body.querySelector("footer").innerText = "Made with suffering, and ofcourse streamlit"
    if (node.nodeName.toLowerCase() === 'p' && node.innerHTML.includes("<script>")) {
        let tempDiv = document.createElement('div');
        tempDiv.innerHTML = node.innerHTML;
        let scriptTags = tempDiv.getElementsByTagName('script');
        Array.from(scriptTags).forEach((scriptTag) => {
            let newScript = document.createElement('script');
            if (scriptTag.src) {
                newScript.src = scriptTag.src;
            }
            if (scriptTag.innerHTML) {
                newScript.innerHTML = scriptTag.innerHTML;
            }
            document.body.appendChild(newScript);
        });
        node.parentNode.removeChild(node);
    }
}

let observer = new MutationObserver((mutationsList, observer) => {
    for (let mutation of mutationsList) {
        if (mutation.addedNodes.length) {
            mutation.addedNodes.forEach(checkForScripts);
        }
    }
});

observer.observe(document.body, {childList: true, subtree: true});

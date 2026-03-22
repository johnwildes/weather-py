export function scrollToBottom(element) {
    if (element) {
        requestAnimationFrame(() => { element.scrollTop = element.scrollHeight; });
    }
}

export function focusElement(element) {
    if (element) element.focus();
}

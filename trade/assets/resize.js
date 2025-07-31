document.addEventListener("mousedown", function(e) {
    if (!e.target.id.includes("resize-handle")) return;

    const target = e.target.closest("div[id^='item-']");
    const startX = e.clientX;
    const startWidth = target.offsetWidth;
    const direction = e.target.id.includes("left") ? "left" : "right";

    function onMove(ev) {
        let delta = ev.clientX - startX;
        if (direction === "left") delta = -delta;
        target.style.width = Math.max(60, startWidth + delta) + "px";
    }

    function onUp() {
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onUp);
    }

    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
});

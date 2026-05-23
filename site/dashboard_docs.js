(function () {
    function createElement(tagName, className, textContent) {
        var element = document.createElement(tagName);
        if (className) {
            element.className = className;
        }
        if (typeof textContent === "string") {
            element.textContent = textContent;
        }
        return element;
    }

    function uniqueFlatten(keys, lookup, field) {
        var seen = Object.create(null);
        var values = [];

        keys.forEach(function (key) {
            var item = lookup[key];
            if (!item || !Array.isArray(item[field])) {
                return;
            }

            item[field].forEach(function (value) {
                if (seen[value]) {
                    return;
                }
                seen[value] = true;
                values.push(value);
            });
        });

        return values.sort(function (a, b) {
            return a.localeCompare(b);
        });
    }

    function appendList(body, title, items) {
        if (!Array.isArray(items) || !items.length) {
            return;
        }

        if (title) {
            body.appendChild(createElement("p", "doc-list-title", title));
        }

        var list = createElement("ul", "doc-list");
        items.forEach(function (item) {
            list.appendChild(createElement("li", "", item));
        });
        body.appendChild(list);
    }

    function createAccordion(item) {
        var details = createElement("details", "doc-accordion doc-anchor");
        if (item.id) {
            details.id = item.id;
        }
        if (item.open) {
            details.open = true;
        }
        if (item.accentVar) {
            details.style.setProperty("--docs-accent", item.accentVar);
        }

        var summary = createElement("summary");
        var summaryLine = createElement("span", "doc-summary-line");

        if (item.tag) {
            summaryLine.appendChild(createElement("span", "doc-tag", item.tag));
        }

        summaryLine.appendChild(createElement("span", "doc-summary-title", item.title));
        summary.appendChild(summaryLine);

        if (item.note) {
            summary.appendChild(createElement("span", "doc-summary-note", item.note));
        }

        details.appendChild(summary);

        var body = createElement("div", "doc-body");
        if (item.rule) {
            body.appendChild(createElement("p", "", item.rule));
        }

        (item.paragraphs || []).forEach(function (paragraph) {
            body.appendChild(createElement("p", "", paragraph));
        });

        appendList(body, item.listTitle, item.list);
        details.appendChild(body);
        return details;
    }

    function renderSectionDocs(host, items) {
        host.innerHTML = "";
        var wrapper = createElement("div", "section-docs");
        items.forEach(function (item) {
            wrapper.appendChild(createAccordion(item));
        });
        host.appendChild(wrapper);
        return host;
    }

    function renderDocsPanel(host, config) {
        host.innerHTML = "";
        host.classList.add("docs-panel");

        host.appendChild(createElement("h2", "docs-title", config.title));
        if (config.intro) {
            host.appendChild(createElement("p", "docs-intro", config.intro));
        }

        var stack = createElement("div", "docs-stack");
        config.items.forEach(function (item) {
            stack.appendChild(createAccordion(item));
        });
        host.appendChild(stack);
        return host;
    }

    function openHashTarget(hash) {
        if (!hash || hash.charAt(0) !== "#") {
            return;
        }

        var target = document.querySelector(hash);
        if (!target) {
            return;
        }

        if (target.tagName && target.tagName.toLowerCase() === "details") {
            target.open = true;
        }

        var parentDetails = target.closest("details");
        if (parentDetails) {
            parentDetails.open = true;
        }
    }

    function setupInlineDocLinks(root) {
        (root || document).querySelectorAll(".doc-link").forEach(function (link) {
            var href = link.getAttribute("href") || "";
            var hashIndex = href.indexOf("#");
            if (hashIndex >= 0) {
                link.setAttribute("href", href.slice(hashIndex));
            }

            link.addEventListener("click", function (event) {
                event.stopPropagation();

                var targetHash = link.getAttribute("href") || "";
                if (targetHash.charAt(0) !== "#") {
                    return;
                }

                event.preventDefault();
                openHashTarget(targetHash);

                var target = document.querySelector(targetHash);
                if (target) {
                    var sidebar = target.closest(".sidebar");
                    if (sidebar) {
                        var targetBox = target.getBoundingClientRect();
                        var sidebarBox = sidebar.getBoundingClientRect();
                        var targetTop = sidebar.scrollTop + (targetBox.top - sidebarBox.top) - 12;
                        sidebar.scrollTo({ top: Math.max(0, targetTop), behavior: "smooth" });
                    } else {
                        target.scrollIntoView({ behavior: "smooth", block: "start" });
                    }
                }

                if (window.history && window.history.replaceState) {
                    window.history.replaceState(null, "", targetHash);
                } else {
                    window.location.hash = targetHash;
                }
            });
        });
    }

    window.addEventListener("hashchange", function () {
        openHashTarget(window.location.hash);
    });

    window.DashboardDocs = {
        uniqueFlatten: uniqueFlatten,
        renderDocsPanel: renderDocsPanel,
        renderSectionDocs: renderSectionDocs,
        setupInlineDocLinks: setupInlineDocLinks,
        openHashTarget: openHashTarget
    };
}());

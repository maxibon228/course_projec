document.addEventListener("DOMContentLoaded", () => {
    // -----------------------------
    // 1. Переключение темы
    // -----------------------------
    // В новой версии используется кнопка #themeToggle.
    // .theme-dot оставлен как запасной вариант, если пользователь случайно открыл старый HTML.
    const themeToggle = document.querySelector("#themeToggle") || document.querySelector(".theme-dot");
    const themeIcon = document.querySelector("#themeIcon") || themeToggle;

    const getSavedTheme = () => {
        try {
            return localStorage.getItem("theme") || "dark";
        } catch (error) {
            return "dark";
        }
    };

    const saveTheme = (theme) => {
        try {
            localStorage.setItem("theme", theme);
        } catch (error) {
            // Даже если localStorage недоступен, тема применится до перезагрузки страницы.
        }
    };

    const applyTheme = (theme) => {
        const normalizedTheme = theme === "light" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", normalizedTheme);
        document.documentElement.dataset.theme = normalizedTheme;
        if (document.body) {
            document.body.setAttribute("data-theme", normalizedTheme);
        }
        saveTheme(normalizedTheme);

        if (themeIcon) {
            themeIcon.textContent = normalizedTheme === "light" ? "☀" : "☾";
        }
    };

    applyTheme(getSavedTheme());

    if (themeToggle) {
        themeToggle.setAttribute("role", "button");
        themeToggle.setAttribute("tabindex", "0");
        themeToggle.setAttribute("title", "Переключить тему");

        const toggleTheme = () => {
            const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
            const nextTheme = currentTheme === "dark" ? "light" : "dark";
            applyTheme(nextTheme);
        };

        themeToggle.addEventListener("click", toggleTheme);
        themeToggle.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                toggleTheme();
            }
        });
    }

    // -----------------------------
    // 2. Сворачивание и разворачивание sidebar
    // -----------------------------
    const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
    const sidebar = document.querySelector("#sidebar");

    const getSavedSidebarState = () => {
        try {
            return localStorage.getItem("sidebar-collapsed") === "true";
        } catch (error) {
            return false;
        }
    };

    const saveSidebarState = (isCollapsed) => {
        try {
            localStorage.setItem("sidebar-collapsed", String(isCollapsed));
        } catch (error) {
            // Без localStorage меню всё равно работает до перезагрузки страницы.
        }
    };

    const applySidebarState = (isCollapsed) => {
        document.documentElement.classList.toggle("sidebar-collapsed", isCollapsed);
        if (document.body) {
            document.body.classList.toggle("sidebar-collapsed", isCollapsed);
        }
        if (sidebarToggle) {
            sidebarToggle.setAttribute("aria-expanded", String(!isCollapsed));
            sidebarToggle.setAttribute(
                "title",
                isCollapsed ? "Развернуть меню" : "Свернуть меню"
            );
        }
        if (sidebar) {
            sidebar.dataset.collapsed = String(isCollapsed);
        }
        saveSidebarState(isCollapsed);
    };

    applySidebarState(getSavedSidebarState());

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", () => {
            const isCollapsed = document.documentElement.classList.contains("sidebar-collapsed");
            applySidebarState(!isCollapsed);
        });
    }

    // -----------------------------
    // 3. Счётчик символов textarea
    // -----------------------------
    const textarea = document.querySelector("[data-message-input]");
    const counter = document.querySelector("[data-char-counter]");

    if (textarea && counter) {
        const maxLength = Number(textarea.getAttribute("maxlength")) || 2000;
        const updateCounter = () => {
            counter.textContent = `${textarea.value.length} / ${maxLength}`;
        };

        textarea.addEventListener("input", updateCounter);
        updateCounter();
    }

    // -----------------------------
    // 4. Поиск по таблице сообщений
    // -----------------------------
    const searchInput = document.querySelector("[data-table-search]");
    const rows = Array.from(document.querySelectorAll("[data-message-row]"));
    const emptySearch = document.querySelector("[data-search-empty]");

    if (searchInput && rows.length > 0) {
        searchInput.addEventListener("input", () => {
            const query = searchInput.value.trim().toLowerCase();
            let visibleCount = 0;

            rows.forEach((row) => {
                const source = row.dataset.search || row.textContent.toLowerCase();
                const isVisible = source.includes(query);
                row.classList.toggle("hidden", !isVisible);
                if (isVisible) {
                    visibleCount += 1;
                }
            });

            if (emptySearch) {
                emptySearch.classList.toggle("hidden", visibleCount !== 0);
            }
        });
    }

    // -----------------------------
    // 5. Плавная вертикальная прокрутка карточек алгоритмов
    // -----------------------------
    const algorithmScroll = document.querySelector("[data-algorithm-scroll]");
    if (algorithmScroll) {
        algorithmScroll.style.scrollBehavior = "smooth";
        algorithmScroll.addEventListener("wheel", (event) => {
            if (Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
                algorithmScroll.scrollTop += event.deltaY;
            }
        }, { passive: true });
    }

    // -----------------------------
    // 6. Лёгкая анимация появления карточек
    // -----------------------------
    document.querySelectorAll(".reveal").forEach((element, index) => {
        element.style.animationDelay = `${Math.min(index * 0.06, 0.42)}s`;
    });
});

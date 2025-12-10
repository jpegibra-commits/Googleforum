// Скрипт для управления темами приложения

// Функция для установки темы
function setTheme(themeName) {
  // Устанавливаем атрибут data-theme на html элемент
  document.documentElement.setAttribute("data-theme", themeName)

  // Сохраняем выбор пользователя в localStorage
  localStorage.setItem("theme", themeName)

  // Обновляем текст кнопки
  updateThemeButtonText()
}

// Функция для обновления текста кнопки переключения темы
function updateThemeButtonText() {
  const themeButton = document.getElementById("theme-toggle")
  if (!themeButton) return

  themeButton.textContent = "Выбрать тему"
}

// Функция для переключения выпадающего меню тем
function toggleThemeDropdown() {
  const dropdown = document.getElementById("theme-dropdown")
  if (dropdown) {
    dropdown.classList.toggle("show")
  }
}

// Функция для закрытия выпадающего меню при клике вне его
function closeThemeDropdown(event) {
  const dropdown = document.getElementById("theme-dropdown")
  const button = document.getElementById("theme-toggle")

  if (dropdown && dropdown.classList.contains("show") && !dropdown.contains(event.target) && event.target !== button) {
    dropdown.classList.remove("show")
  }
}

// Инициализация темы при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  // Получаем сохраненную тему из localStorage или используем светлую тему по умолчанию
  const savedTheme = localStorage.getItem("theme") || "light"

  // Устанавливаем сохраненную тему
  setTheme(savedTheme)

  // Добавляем обработчик для кнопки переключения темы
  const themeButton = document.getElementById("theme-toggle")
  if (themeButton) {
    themeButton.addEventListener("click", toggleThemeDropdown)
  }

  // Добавляем обработчики для опций тем
  const themeOptions = document.querySelectorAll(".theme-option")
  themeOptions.forEach((option) => {
    option.addEventListener("click", function () {
      const theme = this.getAttribute("data-theme")
      setTheme(theme)
      toggleThemeDropdown() // Закрываем выпадающее меню после выбора
    })
  })

  // Закрываем выпадающее меню при клике вне его
  document.addEventListener("click", closeThemeDropdown)
})

// Скрипт для работы с камерой и местоположением
console.log("Скрипт загружен")

// Функция для форматирования координат
function formatCoordinates(latitude, longitude) {
  return `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`
}

// Функция для расчета расстояния между двумя точками (в километрах)
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371 // Радиус Земли в км
  const dLat = ((lat2 - lat1) * Math.PI) / 180
  const dLon = ((lon2 - lon1) * Math.PI) / 180
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  const distance = R * c
  return distance
}

// Функция для проверки поддержки камеры
function checkCameraSupport() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    console.log("Камера поддерживается в этом браузере")
    return true
  } else {
    console.log("Камера не поддерживается в этом браузере")
    return false
  }
}

// Функция для проверки поддержки геолокации
function checkLocationSupport() {
  if (navigator.geolocation) {
    console.log("Геолокация поддерживается в этом браузере")
    return true
  } else {
    console.log("Геолокация не поддерживается в этом браузере")
    return false
  }
}

// Проверяем поддержку функций при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  checkCameraSupport()
  checkLocationSupport()
})

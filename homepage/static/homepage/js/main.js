/* Небольшая клиентская часть интерфейса: текущий год в подвале.
   Год не записан в HTML — его подставляет браузер. */

const yearElement = document.getElementById("current-year");

if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
}

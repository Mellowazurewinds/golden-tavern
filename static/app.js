const grid = document.querySelector("#recipe-grid");
const form = document.querySelector("#search-form");
const input = document.querySelector("#search-input");
const status = document.querySelector("#status-message");
const resultsTitle = document.querySelector("#results-title");
const resultsCount = document.querySelector("#results-count");
const clearButton = document.querySelector(".clear-button");
const dialog = document.querySelector("#recipe-dialog");
const dialogContent = document.querySelector("#dialog-content");

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}

function setLoading(message) {
  status.textContent = message;
  status.hidden = false;
  grid.replaceChildren();
  resultsCount.textContent = "";
}

function renderMeals(meals, heading) {
  resultsTitle.textContent = heading;
  status.hidden = true;
  resultsCount.textContent = `${meals.length} ${meals.length === 1 ? "recipe" : "recipes"}`;
  grid.innerHTML = meals.map((meal, index) => `
    <article class="recipe-card" style="--card-order:${index}">
      <button class="recipe-open" type="button" data-meal-id="${escapeHtml(meal.idMeal)}" aria-label="View ${escapeHtml(meal.strMeal)} recipe">
        <span class="card-image-wrap"><img class="card-image" src="${escapeHtml(meal.strMealThumb)}" alt="${escapeHtml(meal.strMeal)}" loading="lazy"><span class="card-number">${String(index + 1).padStart(2, "0")}</span><span class="card-arrow" aria-hidden="true">↗</span></span>
        <span class="card-meta">${escapeHtml(meal.strArea || "FROM THE RECIPE BOX")} <span>·</span> ${escapeHtml(meal.strCategory || "A GOOD IDEA")}</span>
        <span class="card-title">${escapeHtml(meal.strMeal)}</span>
      </button>
    </article>`).join("");
}

async function loadMeals(query, { random = false, category = "" } = {}) {
  setLoading(random ? "Asking the kitchen…" : "Looking through the recipe box…");
  resultsTitle.textContent = random ? "Tonight’s little surprise" : query ? `Good things with ${query}` : "A little inspiration";
  const endpoint = random ? "/api/meals/random" : category ? `/api/categories/${encodeURIComponent(category)}` : `/api/meals?q=${encodeURIComponent(query)}`;
  try {
    const response = await fetch(endpoint);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Something went wrong. Please try again.");
    const meals = payload.meals || [];
    if (!meals.length) {
      resultsTitle.textContent = query ? `Nothing found for “${query}”` : "A little inspiration";
      status.textContent = "Try another ingredient or dish. There’s always something good in the recipe box.";
      status.hidden = false;
      resultsCount.textContent = "";
      return;
    }
    renderMeals(meals.slice(0, 8), random ? "Tonight’s little surprise" : category || (query ? `Good things with ${query}` : "A little inspiration"));
  } catch (error) {
    status.textContent = error.message || "We couldn’t reach the recipe box. Please try again.";
    status.hidden = false;
    resultsCount.textContent = "";
  }
}

function ingredientsFor(meal) {
  return Array.from({ length: 20 }, (_, index) => {
    const number = index + 1;
    const ingredient = meal[`strIngredient${number}`]?.trim();
    const measure = meal[`strMeasure${number}`]?.trim();
    return ingredient ? `<li><span>${escapeHtml(ingredient)}</span><span>${escapeHtml(measure)}</span></li>` : "";
  }).filter(Boolean).join("");
}

async function openRecipe(id) {
  dialogContent.innerHTML = '<p class="dialog-loading">Opening the recipe…</p>';
  dialog.showModal();
  try {
    const response = await fetch(`/api/meals/${encodeURIComponent(id)}`);
    const meal = await response.json();
    if (!response.ok) throw new Error(meal.error || "Recipe could not be opened.");
    const steps = (meal.strInstructions || "").split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
    dialogContent.innerHTML = `
      <img class="dialog-image" src="${escapeHtml(meal.strMealThumb)}" alt="${escapeHtml(meal.strMeal)}">
      <div class="dialog-body"><p class="eyebrow"><span></span> ${escapeHtml(meal.strArea || "FROM THE RECIPE BOX")} · ${escapeHtml(meal.strCategory || "GOOD FOOD")}</p>
      <h2 id="dialog-title">${escapeHtml(meal.strMeal)}</h2>
      <div class="detail-columns"><section><h3>What you’ll need</h3><ul class="ingredient-list">${ingredientsFor(meal)}</ul></section><section><h3>Let’s make it</h3><ol class="step-list">${steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol></section></div>
      ${meal.strSource ? `<a class="source-link" href="${escapeHtml(meal.strSource)}" target="_blank" rel="noreferrer">Original recipe <span aria-hidden="true">↗</span></a>` : ""}</div>`;
  } catch (error) {
    dialogContent.innerHTML = `<div class="dialog-body"><p class="eyebrow"><span></span> RECIPE BOX</p><h2 id="dialog-title">A small hiccup</h2><p>${escapeHtml(error.message)}</p></div>`;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const query = input.value.trim();
  if (query) loadMeals(query);
});

document.querySelectorAll(".chip").forEach((button) => button.addEventListener("click", () => {
  input.value = button.dataset.query || "";
  clearButton.hidden = !input.value;
  loadMeals(button.dataset.query || button.dataset.category, { category: button.dataset.category || "" });
}));

document.querySelector("#surprise-button").addEventListener("click", () => loadMeals("", { random: true }));
clearButton.addEventListener("click", () => { input.value = ""; clearButton.hidden = true; input.focus(); });
input.addEventListener("input", () => { clearButton.hidden = !input.value; });
grid.addEventListener("click", (event) => {
  const button = event.target.closest("[data-meal-id]");
  if (button) openRecipe(button.dataset.mealId);
});
document.querySelector("#dialog-close").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });

loadMeals("chicken");

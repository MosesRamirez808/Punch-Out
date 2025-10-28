function searchBible() {
  const query = document.getElementById("query").value.trim().toLowerCase();
  const resultsContainer = document.getElementById("results");
  resultsContainer.innerHTML = "";

  if (!query) {
    resultsContainer.innerHTML = "Please enter a word or phrase.";
    return;
  }

  if (Object.keys(bibleData).length === 0) {
    resultsContainer.innerHTML = "⏳ Bible still loading. Please wait.";
    return;
  }

  let results = [];

  for (let book in bibleData) {
    for (let chapter in bibleData[book]) {
      for (let verse in bibleData[book][chapter]) {
        const text = bibleData[book][chapter][verse];
        if (text.toLowerCase().includes(query)) {
          const highlightedText = text.replace(
            new RegExp(query, 'gi'),
            match => `<mark>${match}</mark>`
          );
          results.push(`<strong>${book} ${chapter}:${verse}</strong> - ${highlightedText}`);
        }
      }
    }
  }

  console.log("Search results found:", results.length);

  resultsContainer.innerHTML = results.length
    ? results.join("<br><br>")
    : "❌ No verses found.";
}

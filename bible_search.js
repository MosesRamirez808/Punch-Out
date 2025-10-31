function searchBible() {
  const query = document.getElementById("query").value.trim(); // Keep original casing for passage check
  const resultsContainer = document.getElementById("results");
  resultsContainer.innerHTML = "";

  if (!query) {
    resultsContainer.innerHTML = "Please enter a word, phrase, or passage (e.g., John 3:16).";
    return;
  }

  if (typeof bibleData === "undefined" || Object.keys(bibleData).length === 0) {
    resultsContainer.innerHTML = "⏳ Bible still loading. Please wait.";
    return;
  }

  // ⭐️ Check for direct passage match (e.g., "John 3:16") ⭐️
  const passageResult = getPassage(query);
  if (passageResult) {
    resultsContainer.innerHTML = passageResult;
    console.log("Found direct passage:", query);
    return;
  }

  // Keyword search logic
  const lowerQuery = query.toLowerCase();
  let results = [];
  const searchRegex = new RegExp(lowerQuery, "gi");

  // Loop through all Bible data
  for (let book in bibleData) {
    if (!bibleData.hasOwnProperty(book)) continue;

    for (let chapter in bibleData[book]) {
      if (!bibleData[book].hasOwnProperty(chapter)) continue;

      for (let verse in bibleData[book][chapter]) {
        if (!bibleData[book][chapter].hasOwnProperty(verse)) continue;

        const text = bibleData[book][chapter][verse];
        if (text.toLowerCase().includes(lowerQuery)) {
          const highlightedText = text.replace(
            searchRegex,
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
    : "❌ No verses found for keyword or passage.";
}

/**
 * Helper: getPassage()
 * This should retrieve a specific verse or passage when the user types something like "John 3:16".
 * If you already have this in another file, keep that. 
 * Otherwise, here’s a safe placeholder that avoids runtime errors.
 */
function getPassage(reference) {
  // Basic check for Book Chapter:Verse format
  const passageRegex = /^([1-3]?\s?[A-Za-z]+)\s+(\d+):(\d+)$/;
  const match = reference.match(passageRegex);

  if (!match) return null;

  const [, bookName, chapter, verse] = match;
  const book = Object.keys(bibleData).find(
    b => b.toLowerCase() === bookName.toLowerCase()
  );

  if (book && bibleData[book] && bibleData[book][chapter] && bibleData[book][chapter][verse]) {
    const text = bibleData[book][chapter][verse];
    return `<strong>${book} ${chapter}:${verse}</strong> - ${text}`;
  }

  return null; // not found
}

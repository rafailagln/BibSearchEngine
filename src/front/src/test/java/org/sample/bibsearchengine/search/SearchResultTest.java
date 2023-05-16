package org.sample.bibsearchengine.search;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class SearchResultTest {

    @Test
    void testConstructor() {
        String title = "test_title";
        String url = "test_url";
        String snippet = "test_snippet";

        SearchResult searchResult = new SearchResult(title, url, snippet);

        assertEquals(title, searchResult.getTitle());
        assertEquals(url, searchResult.getUrl());
        assertEquals(snippet, searchResult.getSnippet());
    }

    @Test
    void testSetterAndGetter() {
        SearchResult searchResult = new SearchResult("", "", "");

        String title = "new_title";
        String url = "new_url";
        String snippet = "new_snippet";

        searchResult.setTitle(title);
        searchResult.setUrl(url);
        searchResult.setSnippet(snippet);

        assertEquals(title, searchResult.getTitle());
        assertEquals(url, searchResult.getUrl());
        assertEquals(snippet, searchResult.getSnippet());
    }
}

package org.sample.bibsearchengine.search;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class SearchQueryTest {

    @Test
    void testGetQuery() {
        SearchQuery searchQuery = new SearchQuery();
        String query = "test_query";
        searchQuery.setQuery(query);
        assertEquals(query, searchQuery.getQuery());
    }

    @Test
    void testSetQuery() {
        SearchQuery searchQuery = new SearchQuery();
        String query = "test_query";
        searchQuery.setQuery(query);
        assertEquals(query, searchQuery.getQuery());
    }

    @Test
    void testConstructor() {
        String query = "test_query";
        SearchQuery searchQuery = new SearchQuery(query);
        assertEquals(query, searchQuery.getQuery());
    }
}

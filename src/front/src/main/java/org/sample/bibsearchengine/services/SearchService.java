package org.sample.bibsearchengine.services;

import org.sample.bibsearchengine.api.PythonAPISearch;
import org.sample.bibsearchengine.search.SearchResult;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SearchService {

    public List<SearchResult> search(String query) {
        return  PythonAPISearch.search(query);
    }
}


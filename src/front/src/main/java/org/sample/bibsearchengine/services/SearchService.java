package org.sample.bibsearchengine.services;

import org.sample.bibsearchengine.api.PythonAPISearch;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SearchService {

    public List<Integer> searchIds(String query) {
        return  PythonAPISearch.searchIds(query);
    }

    public List<String> alternativeQueries(String query) {
        return  PythonAPISearch.alternativeQueries(query);
    }

}


package org.sample.bibsearchengine.controllers;

import org.sample.bibsearchengine.api.PythonAPISearch;
import org.sample.bibsearchengine.search.SearchQuery;
import org.sample.bibsearchengine.search.SearchResult;
import org.sample.bibsearchengine.services.SearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;

import java.util.List;

@Controller
public class SearchController {

    @Autowired
    private SearchService searchService;

    @GetMapping("/")
    public String showHomePage(Model model) {
        model.addAttribute("searchQuery", new SearchQuery());
        return "index";
    }

    @GetMapping("/search")
    public String showSearchPage() {
        return "search";
    }

    @PostMapping("/search")
    public String searchResults(@ModelAttribute("searchQuery") SearchQuery searchQuery, Model model) {
        List<SearchResult> results = searchService.search(searchQuery.getQuery());
        model.addAttribute("results", results);
        return "search";
    }
}


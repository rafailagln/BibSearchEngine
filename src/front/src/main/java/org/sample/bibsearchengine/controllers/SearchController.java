package org.sample.bibsearchengine.controllers;

import org.sample.bibsearchengine.search.SearchQuery;
import org.sample.bibsearchengine.services.SearchService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;

import java.util.List;

@Controller
public class SearchController {

    private final SearchService searchService;

    public SearchController(SearchService searchService) {
        if(searchService == null){
            throw new IllegalArgumentException("SearchService cannot be null");
        }
        this.searchService = searchService;
    }

    @GetMapping("/")
    public String showHomePage(Model model) {
        model.addAttribute("searchQuery", new SearchQuery());
        return "index";
    }

    @PostMapping("/search")
    public String searchResults(@ModelAttribute("searchQuery") SearchQuery searchQuery, Model model) {
        if(searchQuery != null && searchQuery.getQuery() != null) {
            try {
                List<Integer> results = searchService.searchIds(searchQuery.getQuery());
                List<String> alternativeQueries = searchService.alternativeQueries(searchQuery.getQuery());
                model.addAttribute("results", results);
                model.addAttribute("alternativeQueries", alternativeQueries);
            } catch (IllegalArgumentException e) {
                // Log error and handle it accordingly
            }
        }
        return "search";
    }
}

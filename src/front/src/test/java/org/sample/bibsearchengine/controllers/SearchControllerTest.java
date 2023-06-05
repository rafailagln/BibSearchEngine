package org.sample.bibsearchengine.controllers;

import org.sample.bibsearchengine.services.SearchService;
import org.sample.bibsearchengine.search.SearchQuery;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class SearchControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private SearchService searchService;

    @Test
    public void testShowHomePage() throws Exception {
        this.mockMvc.perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(view().name("index"))
                .andExpect(model().attributeExists("searchQuery"));
    }

//    @Test
//    public void testSearchResults() throws Exception {
//        List<Integer> results = Arrays.asList(1, 2, 3);
//        List<String> alternativeQueries = Arrays.asList("query1", "query2");
//
//        when(searchService.searchIds(any(String.class))).thenReturn(results);
//        when(searchService.alternativeQueries(any(String.class))).thenReturn(alternativeQueries);
//
//        this.mockMvc.perform(post("/search").param("searchQuery", "test"))
//                .andExpect(status().isOk())
//                .andExpect(view().name("search"))
//                .andExpect(model().attributeExists("results", "alternativeQueries"))
//                .andExpect(model().attribute("results", results))
//                .andExpect(model().attribute("alternativeQueries", alternativeQueries));
//    }

}

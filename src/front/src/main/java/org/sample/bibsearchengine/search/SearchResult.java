package org.sample.bibsearchengine.search;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class SearchResult {

    private String title;
    private String url;
    private String snippet;

    public SearchResult(String title, String url, String snippet) {
        this.title = title;
        this.url = url;
        this.snippet = snippet;
    }

    // getters and setters
}


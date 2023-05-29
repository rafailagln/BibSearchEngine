package org.sample.bibsearchengine.controllers;

import java.util.List;

import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/api")
public class ProxyController {

    @PostMapping("/fetch_data/")
    public ResponseEntity<?> fetchDataForIds(@RequestBody List<String> ids) {
        return callExternalApi(ids);
    }

    private ResponseEntity<String> callExternalApi(List<String> ids) {
        RestTemplate restTemplate = new RestTemplate();
        String externalApiUrl = "http://127.0.0.1:5000/fetch_data/";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<List<String>> requestEntity = new HttpEntity<>(ids, headers);
        return restTemplate.exchange(externalApiUrl, HttpMethod.POST, requestEntity, String.class);
    }
}
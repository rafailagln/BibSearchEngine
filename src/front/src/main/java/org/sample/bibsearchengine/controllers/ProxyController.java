package org.sample.bibsearchengine.controllers;

import java.util.List;
import java.io.IOException;
import java.util.Properties;

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

    private static final String EXTERNAL_API_URL;

    static {
        // load the properties file
        Properties properties = new Properties();
        try {
            properties.load(ProxyController.class.getClassLoader().getResourceAsStream("application.properties"));
            EXTERNAL_API_URL = properties.getProperty("external.api.call");
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    @PostMapping("/fetch_data/")
    public ResponseEntity<?> fetchDataForIds(@RequestBody List<String> ids) {
        return callExternalApi(ids);
    }

    private ResponseEntity<String> callExternalApi(List<String> ids) {
        RestTemplate restTemplate = new RestTemplate();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<List<String>> requestEntity = new HttpEntity<>(ids, headers);
        return restTemplate.exchange(EXTERNAL_API_URL, HttpMethod.POST, requestEntity, String.class);
    }
}

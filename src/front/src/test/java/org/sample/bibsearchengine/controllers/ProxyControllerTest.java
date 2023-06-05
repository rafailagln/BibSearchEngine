//package org.sample.bibsearchengine.controllers;
//
//import org.junit.jupiter.api.BeforeEach;
//import org.junit.jupiter.api.Test;
//import org.mockito.Mock;
//import org.mockito.Mockito;
//import org.mockito.MockitoAnnotations;
//import org.springframework.http.HttpEntity;
//import org.springframework.http.HttpHeaders;
//import org.springframework.http.HttpMethod;
//import org.springframework.http.MediaType;
//import org.springframework.http.ResponseEntity;
//import org.springframework.web.client.HttpClientErrorException;
//import org.springframework.web.client.ResourceAccessException;
//import org.springframework.web.client.RestTemplate;
//import org.springframework.http.HttpStatus;
//
//import java.util.Arrays;
//import java.util.List;
//
//import static org.junit.jupiter.api.Assertions.assertEquals;
//import static org.junit.jupiter.api.Assertions.assertThrows;
//import static org.junit.jupiter.api.Assertions.assertTrue;
//import static org.mockito.Mockito.when;
//
//
//class ProxyControllerTest {
//
//    @Mock
//    private RestTemplate restTemplate;
//
//    private ProxyController proxyController;
//
//    @BeforeEach
//    void setUp() {
//        MockitoAnnotations.openMocks(this);
//        proxyController = new ProxyController();
//    }
//
//    @Test
//    void testFetchDataForIds() {
//        List<String> ids = Arrays.asList("1", "2", "3");
//
//        HttpHeaders headers = new HttpHeaders();
//        headers.setContentType(MediaType.APPLICATION_JSON);
//
//        HttpEntity<List<String>> requestEntity = new HttpEntity<>(ids, headers);
//
//        when(restTemplate.exchange(Mockito.anyString(), Mockito.eq(HttpMethod.POST), Mockito.eq(requestEntity), Mockito.eq(String.class)))
//                .thenThrow(new HttpClientErrorException(HttpStatus.FORBIDDEN, "403 Forbidden"));
//
//        HttpClientErrorException.Forbidden exception = assertThrows(HttpClientErrorException.Forbidden.class, () -> {
//            proxyController.fetchDataForIds(ids);
//        });
//
//        assertTrue(exception.getMessage().startsWith("403 Forbidden"), "Unexpected exception message");
//    }
//
//}

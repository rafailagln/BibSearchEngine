package org.sample.bibsearchengine.controllers;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.io.IOException;
import java.nio.file.Files;

@Controller
public class NodeController {

    @Value("classpath:config.json")
    Resource configResource;

    @GetMapping("/admin")
    public String admin(Model model) throws IOException {
        String config = new String(Files.readAllBytes(configResource.getFile().toPath()));
        model.addAttribute("config", config);
        return "admin";
    }
}

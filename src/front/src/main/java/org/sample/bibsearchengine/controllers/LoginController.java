package org.sample.bibsearchengine.controllers;

import org.sample.bibsearchengine.entities.AppUser;
import org.sample.bibsearchengine.services.UserService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;

@Controller
public class LoginController {

    private final UserService userService;

    public LoginController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/login")
    public String showLoginPage(Model model) {
        model.addAttribute("appUser", new AppUser());
        return "login";
    }

    @PostMapping("/login")
    public String loginUser(@ModelAttribute("user") AppUser appUser, Model model) {
        if (userService.checkUserCredentials(appUser.getUsername(), appUser.getPassword())) {
            return "redirect:/";
        } else {
            model.addAttribute("error", "Invalid username or password");
            return "login";
        }
    }
}


//package org.sample.bibsearchengine.services;
//
//import org.sample.bibsearchengine.entities.AppUser;
//import org.sample.bibsearchengine.repositories.UserRepository;
//import org.springframework.stereotype.Service;
//
//@Service
//public class UserService {
//
//    private final UserRepository userRepository;
//
//    public UserService(UserRepository userRepository) {
//        this.userRepository = userRepository;
//    }
//
//    public boolean checkUserCredentials(String username, String password) {
//        AppUser appUser = userRepository.findByUsername(username);
//        return appUser != null && appUser.getPassword().equals(password);
//    }
//}
//

package org.sample.bibsearchengine.security.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

import static org.springframework.security.config.Customizer.withDefaults;
import static org.springframework.security.web.util.matcher.AntPathRequestMatcher.antMatcher;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .securityMatcher(antMatcher("/ap/**"))
                .authorizeHttpRequests(authorize -> authorize
                        .requestMatchers(antMatcher("/search")).permitAll()
                        .requestMatchers(antMatcher("/index")).permitAll()
                        .requestMatchers(antMatcher("/admin")).permitAll()
                        .requestMatchers(antMatcher("/api/fetch_data")).permitAll()
                        .requestMatchers(antMatcher("/api/update")).permitAll()
                        .anyRequest().authenticated()
                )
                .formLogin(withDefaults());
        return http.build();
    }
}

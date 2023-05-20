package org.sample.bibsearchengine.controllers;

import org.sample.bibsearchengine.entities.NodeStatus;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Sinks;

@RestController
@RequestMapping("/api")
public class NodeStatusController {
    private final Sinks.Many<ServerSentEvent<NodeStatus>> processor = Sinks.many().multicast().onBackpressureBuffer();

    @GetMapping("/sse")
    public Flux<ServerSentEvent<NodeStatus>> getNodeStatusStream() {
        return processor.asFlux();
    }

    @PostMapping("/update")
    public void updateNodeStatus(@RequestBody NodeStatus status) {
        processor.emitNext(ServerSentEvent.<NodeStatus>builder().data(status).build(), Sinks.EmitFailureHandler.FAIL_FAST);
    }
}

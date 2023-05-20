package org.sample.bibsearchengine.entities;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class NodeStatus {
    private int id;
    private boolean online;

    public NodeStatus(int id, boolean online) {
        this.id = id;
        this.online = online;
    }
}

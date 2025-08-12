import React, { useState, useEffect } from "react";

function App() {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [tasks, setTasks] = useState([]);
  const [command, setCommand] = useState("");
  const [interval, setInterval] = useState(0);
  const [enabled, setEnabled] = useState(true);

  const API_BASE = process.env.REACT_APP_API_BASE;

  // Agent listesini API'den çek
  useEffect(() => {
    fetch(`${API_BASE}/agents`)
      .then((res) => res.json())
      .then((data) => setAgents(data))
      .catch(console.error);
  }, []);

  // Agent seçilince görevleri çek
  useEffect(() => {
    if (selectedAgent) {
      fetch(`${API_BASE}/tasks/${selectedAgent}/list`)
        .then((res) => res.json())
        .then((data) => setTasks(data))
        .catch(console.error);
    } else {
      setTasks([]);
    }
  }, [selectedAgent]);

  const addTask = () => {
    if (!selectedAgent || !command) return alert("Agent ve komut gerekli");
    fetch(`${API_BASE}/add_task`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        command,
        target: selectedAgent,
        enabled,
        interval: Number(interval),
      }),
    })
      .then((res) => res.json())
      .then(() => {
        setCommand("");
        setInterval(0);
        setEnabled(true);
        // Görev listesini güncelle
        fetch(`${API_BASE}/tasks/${selectedAgent}/list`)
          .then((res) => res.json())
          .then((data) => setTasks(data));
      });
  };

  const toggleTask = (task) => {
    fetch(
      `${API_BASE}/task/${selectedAgent}/${task.id}/${
        task.enabled ? "disable" : "enable"
      }`,
      { method: "POST" }
    ).then(() => {
      setTasks((tasks) =>
        tasks.map((t) =>
          t.id === task.id ? { ...t, enabled: !t.enabled } : t
        )
      );
    });
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Mehterbash Yönetim Paneli</h1>

      <div>
        <label>Agent Seç: </label>
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
        >
          <option value="">-- Seçin --</option>
          {agents.map((agent) => (
            <option key={agent.id} value={agent.id}>
              {agent.name || agent.id}
            </option>
          ))}
        </select>
      </div>

      <hr />

      <h2>Yeni Görev Ekle</h2>
      <input
        value={command}
        onChange={(e) => setCommand(e.target.value)}
        placeholder="Komut"
      />
      <input
        type="number"
        value={interval}
        onChange={(e) => setInterval(Number(e.target.value))}
        placeholder="Interval (saniye)"
        style={{ width: 120, marginLeft: 10 }}
      />
      <label style={{ marginLeft: 10 }}>
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => setEnabled(e.target.checked)}
        />{" "}
        Aktif
      </label>
      <button onClick={addTask} style={{ marginLeft: 10 }}>
        Görev Ekle
      </button>

      <hr />

      <h2>Görevler ({selectedAgent || "Seçilmedi"})</h2>
      <ul>
        {tasks.map((task) => (
          <li key={task.id} style={{ marginBottom: 8 }}>
            <b>{task.command}</b>{" "}
            [{task.enabled ? "Aktif" : "Pasif"}] — Interval:{" "}
            {task.interval}s{" "}
            <button onClick={() => toggleTask(task)} style={{ marginLeft: 10 }}>
              {task.enabled ? "Disable" : "Enable"}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;

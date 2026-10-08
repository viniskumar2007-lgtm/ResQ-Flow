import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../services/api";

import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

/* =========================================
   TEMPORARY DEMO DATA
========================================= */

const demoIncidents = [
  {
    id: 12,
    disaster_type: "FLOOD",
    severity: "CRITICAL",
    priority_score: 95,
    status: "NEW",
    people_affected: 6,
    latitude: 11.0168,
    longitude: 76.9558,
  },
  {
    id: 11,
    disaster_type: "FLOOD",
    severity: "CRITICAL",
    priority_score: 92,
    status: "ASSIGNED",
    people_affected: 4,
  },
  {
    id: 10,
    disaster_type: "FLOOD",
    severity: "HIGH",
    priority_score: 85,
    status: "NEW",
    people_affected: 2,
  },
  {
    id: 7,
    disaster_type: "FLOOD",
    severity: "HIGH",
    priority_score: 78,
    status: "RESCUED",
    people_affected: 6,
  },
  {
    id: 6,
    disaster_type: "FLOOD",
    severity: "HIGH",
    priority_score: 72,
    status: "ASSIGNED",
    people_affected: 3,
  },
  {
    id: 5,
    disaster_type: "FLOOD",
    severity: "CRITICAL",
    priority_score: 90,
    status: "RESOLVED",
    people_affected: 5,
  },
  {
    id: 4,
    disaster_type: "FLOOD",
    severity: "HIGH",
    priority_score: 70,
    status: "RESOLVED",
    people_affected: 4,
  },
  {
    id: 3,
    disaster_type: "FLOOD",
    severity: "HIGH",
    priority_score: 68,
    status: "CLOSED",
    people_affected: 2,
  },
  {
    id: 2,
    disaster_type: "FLOOD",
    severity: "CRITICAL",
    priority_score: 88,
    status: "NEW",
    people_affected: 7,
  },
  {
    id: 1,
    disaster_type: "FLOOD",
    severity: "HIGH",
    priority_score: 65,
    status: "RESCUED",
    people_affected: 3,
  },
];

/* =========================================
   DASHBOARD
========================================= */

const Dashboard = () => {
  const { user } = useAuth();

  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [demoMode, setDemoMode] = useState(false);

  /* =======================================
     FETCH INCIDENTS
  ======================================= */

 /* =======================================
   DEMO MODE
======================================= */

useEffect(() => {
  let mounted = true;

  const fetchIncidents = async () => {
    try {
      const data = await apiRequest("/api/incidents");

      if (mounted) {
        setIncidents(data.incidents || []);
        setDemoMode(false);
      }
    } catch (error) {
      console.error("Failed to fetch incidents:", error);

      if (mounted) {
        setDemoMode(true);
      }
    } finally {
      if (mounted) {
        setLoading(false);
      }
    }
  };

  fetchIncidents();

  // Refresh every 2 seconds so new SOS alerts appear quickly
  const interval = setInterval(fetchIncidents, 2000);

  return () => {
    mounted = false;
    clearInterval(interval);
  };
}, []);

  /* =======================================
     STATISTICS
  ======================================= */

  const totalIncidents =
    incidents.length;

  const criticalIncidents =
    incidents.filter(
      (incident) =>
        String(
          incident.severity || ""
        ).toUpperCase() === "CRITICAL"
    );

  const criticalCount =
    criticalIncidents.length;

  const activeIncidents =
    incidents.filter(
      (incident) =>
        ![
          "RESCUED",
          "RESOLVED",
          "CLOSED",
        ].includes(
          String(
            incident.status || ""
          ).toUpperCase()
        )
    ).length;

  const resolvedIncidents =
    incidents.filter(
      (incident) =>
        [
          "RESCUED",
          "RESOLVED",
          "CLOSED",
        ].includes(
          String(
            incident.status || ""
          ).toUpperCase()
        )
    ).length;

  /* =======================================
     TOTAL PEOPLE AFFECTED
  ======================================= */

  const totalPeopleAffected =
    incidents.reduce(
      (total, incident) =>
        total +
        Number(
          incident.people_count ??
            incident.people_affected ??
            0
        ),
      0
    );

    /* =======================================
   RESOURCE AVAILABILITY
======================================= */

const resourceAvailability = [
  {
    name: "Rescue Teams",
    icon: "👨‍🚒",
    available: 12,
    total: 15,
  },
  {
    name: "Ambulances",
    icon: "🚑",
    available: 8,
    total: 10,
  },
  {
    name: "Medical Teams",
    icon: "🏥",
    available: 6,
    total: 8,
  },
  {
    name: "Rescue Vehicles",
    icon: "🚒",
    available: 5,
    total: 7,
  },
  {
    name: "Rescue Boats",
    icon: "🚤",
    available: 3,
    total: 4,
  },
];
/* =======================================
   LIVE MAP INCIDENTS
======================================= */

const mapIncidents = incidents.filter((incident) => {
  const latitude = Number(incident.latitude);
  const longitude = Number(incident.longitude);

  return (
    Number.isFinite(latitude) &&
    Number.isFinite(longitude)
  );
});

const mapCenter =
  mapIncidents.length > 0
    ? [
        Number(mapIncidents[0].latitude),
        Number(mapIncidents[0].longitude),
      ]
    : [11.0168, 76.9558];
    /* =======================================
   AI PRIORITY QUEUE
======================================= */

const priorityQueue = [...incidents]
  .filter(
    (incident) =>
      ![
        "RESCUED",
        "RESOLVED",
        "CLOSED",
      ].includes(
        String(
          incident.status || ""
        ).toUpperCase()
      )
  )
  .sort(
    (a, b) =>
      Number(b.priority_score || 0) -
      Number(a.priority_score || 0)
  )
  .slice(0, 5);
  /* =======================================
     RENDER
  ======================================= */

  return (
    <div className="dashboard-page">

      {/* ===================================
          DEMO MODE NOTICE
      ==================================== */}

      {demoMode && (
        <div className="demo-notice">
          <span>●</span>

          Backend unavailable — showing
          demonstration data
        </div>
      )}

      {/* ===================================
          WELCOME
      ==================================== */}

      <section className="welcome-section">

        <div>
          <span className="section-label">
            RESQ-FLOW COMMAND CENTER
          </span>

          <h2>
            Emergency Response Overview
          </h2>

          <p>
            Monitor active emergencies and
            coordinate rescue operations.
          </p>
        </div>

        <Link
          to="/incidents"
          className="primary-action"
        >
          View All Incidents →
        </Link>

      </section>

      {/* ===================================
          STEP 1 — CRITICAL ALERT
      ==================================== */}

      {!loading && criticalCount > 0 && (
        <section className="critical-alert">

          <div className="critical-alert-left">

            <div className="critical-alert-icon">
              !
            </div>

            <div>
              <span className="critical-alert-label">
                CRITICAL EMERGENCY ALERT
              </span>

              <h3>
                {criticalCount} critical{" "}
                {criticalCount === 1
                  ? "incident"
                  : "incidents"}{" "}
                require immediate attention
              </h3>

              <p>
                Rescue operators should review
                these incidents and prioritize
                the required response resources.
              </p>
            </div>

          </div>

          <Link
            to="/incidents"
            className="critical-alert-button"
          >
            View Critical Incidents →
          </Link>

        </section>
      )}

      {/* ===================================
          NO CRITICAL INCIDENTS
      ==================================== */}

      {!loading && criticalCount === 0 && (
        <section className="critical-alert critical-alert-safe">

          <div className="critical-alert-left">

            <div className="critical-alert-icon">
              ✓
            </div>

            <div>
              <span className="critical-alert-label">
                SYSTEM CLEAR
              </span>

              <h3>
                No critical incidents currently
              </h3>

              <p>
                There are no emergencies requiring
                immediate critical response.
              </p>
            </div>

          </div>

        </section>
      )}

      {/* ===================================
          STATISTICS
      ==================================== */}

      <section className="stats-grid">

        {/* TOTAL */}

        <div className="stat-card">

          <div className="stat-icon">
            ⚠
          </div>

          <div>
            <span>
              Total Incidents
            </span>

            <strong>
              {loading
                ? "..."
                : totalIncidents}
            </strong>

            <small>
              Reported emergencies
            </small>
          </div>

        </div>

        {/* CRITICAL */}

        <div className="stat-card critical">

          <div className="stat-icon">
            !
          </div>

          <div>
            <span>
              Critical Incidents
            </span>

            <strong>
              {loading
                ? "..."
                : criticalCount}
            </strong>

            <small>
              Immediate attention required
            </small>
          </div>

        </div>

        {/* ACTIVE */}

        <div className="stat-card active">

          <div className="stat-icon">
            ◉
          </div>

          <div>
            <span>
              Active Incidents
            </span>

            <strong>
              {loading
                ? "..."
                : activeIncidents}
            </strong>

            <small>
              Currently being handled
            </small>
          </div>

        </div>

        {/* RESOLVED */}

        <div className="stat-card rescued">

          <div className="stat-icon">
            ✓
          </div>

          <div>
            <span>
              Resolved
            </span>

            <strong>
              {loading
                ? "..."
                : resolvedIncidents}
            </strong>

            <small>
              Successfully completed
            </small>
          </div>

        </div>

      </section>

      {/* ===================================
          EXTRA STATISTICS
      ==================================== */}

      <section className="stats-grid dashboard-extra-stats">

        <div className="stat-card people-stat">

          <div className="stat-icon">
            👥
          </div>

          <div>
            <span>
              People Affected
            </span>

            <strong>
              {loading
                ? "..."
                : totalPeopleAffected}
            </strong>

            <small>
              People requiring assistance
            </small>
          </div>

        </div>

        <div className="stat-card">

          <div className="stat-icon">
            🤖
          </div>

          <div>
            <span>
              AI Monitoring
            </span>

            <strong>
              Active
            </strong>

            <small>
              Emergency analysis enabled
            </small>
          </div>

        </div>

      </section>

      {/* ===================================
          MAIN DASHBOARD PANELS
      ==================================== */}

      <section className="dashboard-grid">
        {/* =================================
    AI PRIORITY QUEUE
================================== */}
{/* =================================
    RESOURCE AVAILABILITY
================================== */}

<div className="dashboard-panel resource-availability-panel">

  <div className="panel-header">
    <div>
      <span className="section-label">
        RESOURCES
      </span>

      <h3>Resource Availability</h3>

      <p>
        Current emergency response resources.
      </p>
    </div>

    <span className="resource-status">
      LIVE
    </span>
  </div>

  <div className="resource-list">

    {resourceAvailability.map((resource) => {

      const percentage =
        (resource.available / resource.total) * 100;

      return (
        <div
          key={resource.name}
          className="resource-item"
        >

          <div className="resource-icon">
            {resource.icon}
          </div>

          <div className="resource-info">

            <div className="resource-title-row">

              <strong>
                {resource.name}
              </strong>

              <span>
                {resource.available} / {resource.total}
              </span>

            </div>

            <div className="resource-bar">

              <div
                className={`resource-bar-fill ${
                  percentage <= 40
                    ? "resource-low"
                    : percentage <= 70
                    ? "resource-medium"
                    : "resource-good"
                }`}
                style={{
                  width: `${percentage}%`,
                }}
              />

            </div>

          </div>

        </div>
      );
    })}

  </div>

</div>

<div className="dashboard-panel priority-panel">
{/* =================================
    LIVE EMERGENCY MAP
================================== */}

<div className="dashboard-panel emergency-map-panel">

  <div className="panel-header">

    <div>
      <span className="section-label">
        LIVE OPERATIONS
      </span>

      <h3>Live Emergency Map</h3>

      <p>
        Current emergency incidents by GPS location.
      </p>
    </div>

    <div className="map-header-right">

      <span className="map-active-count">
        {activeIncidents} ACTIVE
      </span>

      <Link
        to="/map"
        className="map-full-button"
      >
        Full Map →
      </Link>

    </div>

  </div>

  <div className="dashboard-map">

    <MapContainer
      center={mapCenter}
      zoom={11}
      scrollWheelZoom={false}
      style={{
        width: "100%",
        height: "100%",
      }}
    >

      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {mapIncidents.map((incident) => {

        const severity =
          String(
            incident.severity || ""
          ).toUpperCase();

        const markerColor =
          severity === "CRITICAL"
            ? "#dc2626"
            : severity === "HIGH"
            ? "#ea580c"
            : severity === "MEDIUM"
            ? "#ca8a04"
            : "#16a34a";

        return (
          <CircleMarker
            key={incident.id}
            center={[
              Number(incident.latitude),
              Number(incident.longitude),
            ]}
            radius={
              severity === "CRITICAL"
                ? 11
                : 8
            }
            pathOptions={{
              color: markerColor,
              fillColor: markerColor,
              fillOpacity: 0.75,
              weight: 3,
            }}
          >

            <Popup>

              <strong>
                Incident #{incident.id}
              </strong>

              <br />

              Type:{" "}
              {incident.disaster_type ||
                "Emergency"}

              <br />

              Severity:{" "}
              {severity || "UNKNOWN"}

              <br />

              People:{" "}
              {incident.people_count ??
                incident.people_affected ??
                0}

              <br />
              <br />

              <Link
                to={`/incidents/${incident.id}`}
                state={{
                  incident: incident,
                }}
              >
                View Incident →
              </Link>

            </Popup>

          </CircleMarker>
        );
      })}

    </MapContainer>

  </div>

  <div className="map-footer">

    <div className="map-legend">

      <span>
        <i className="legend-dot critical"></i>
        Critical
      </span>

      <span>
        <i className="legend-dot high"></i>
        High
      </span>

      <span>
        <i className="legend-dot medium"></i>
        Medium
      </span>

      <span>
        <i className="legend-dot low"></i>
        Low
      </span>

    </div>

    <Link to="/map">
      Open Rescue Map →
    </Link>

  </div>

</div>
  <div className="panel-header">

    <div>

      <span className="section-label">
        AI RESPONSE
      </span>

      <h3>
        AI Priority Queue
      </h3>

      <p>
        Incidents recommended for immediate
        attention.
      </p>

    </div>

    <span className="ai-label">
      AI
    </span>

  </div>

  <div className="priority-list">

    {loading ? (

      <div className="priority-empty">
        <p>
          Analyzing incidents...
        </p>
      </div>

    ) : priorityQueue.length === 0 ? (

      <div className="priority-empty">
        <span>✓</span>

        <p>
          No active incidents require
          prioritization.
        </p>
      </div>

    ) : (

      priorityQueue.map(
        (incident, index) => {

          const severity =
            String(
              incident.severity || ""
            ).toUpperCase();

          const priority =
            Number(
              incident.priority_score || 0
            );

          return (
            <div
              key={incident.id}
              className="priority-item"
            >

              {/* RANK */}

              <div className="priority-rank">
                #{index + 1}
              </div>

              {/* SEVERITY INDICATOR */}

              <div
                className={`priority-indicator ${
                  severity === "CRITICAL"
                    ? "priority-critical"
                    : severity === "HIGH"
                    ? "priority-high"
                    : "priority-normal"
                }`}
              ></div>

              {/* INCIDENT INFO */}

              <div className="priority-info">

                <strong>
                  Incident #{incident.id}
                </strong>

                <span>
                  {incident.disaster_type ||
                    "Emergency"}
                </span>

              </div>

              {/* SCORE */}

              <div className="priority-score-box">

                <span>
                  Priority
                </span>

                <strong>
                  {priority}
                </strong>

              </div>

              {/* VIEW */}

              <Link
                to={`/incidents/${incident.id}`}
                state={{
                  incident: incident,
                }}
                className="priority-view"
              >
                View →
              </Link>

            </div>
          );
        }
      )

    )}

  </div>

  {priorityQueue.length > 0 && (
    <div className="priority-footer">

      <span>
        AI recommends responding to{" "}
        <strong>
          Incident #{priorityQueue[0].id}
        </strong>{" "}
        first.
      </span>

      <Link to="/incidents">
        View All →
      </Link>

    </div>
  )}

</div>

        {/* =================================
            RESCUE OPERATIONS
        ================================== */}

        <div className="dashboard-panel">

          <div className="panel-header">

            <div>

              <span className="section-label">
                OPERATIONS
              </span>

              <h3>
                Rescue Operations
              </h3>

              <p>
                Quick access to emergency
                coordination tools.
              </p>

            </div>

          </div>

          <div className="quick-actions">

            {/* INCIDENTS */}

            <Link
              to="/incidents"
              className="quick-action"
            >

              <span className="quick-icon">
                ⚠
              </span>

              <div>
                <strong>
                  Incidents
                </strong>

                <small>
                  View and manage emergencies
                </small>
              </div>

              <span className="quick-arrow">
                →
              </span>

            </Link>

            {/* MAP */}

            <Link
              to="/map"
              className="quick-action"
            >

              <span className="quick-icon">
                ⌖
              </span>

              <div>
                <strong>
                  Rescue Map
                </strong>

                <small>
                  View emergency locations
                </small>
              </div>

              <span className="quick-arrow">
                →
              </span>

            </Link>

          </div>

        </div>

        {/* =================================
            SYSTEM STATUS
        ================================== */}

        <div className="dashboard-panel system-panel">

          <div className="panel-header">

            <div>

              <span className="section-label">
                SYSTEM
              </span>

              <h3>
                System Status
              </h3>

              <p>
                ResQ-Flow operational status.
              </p>

            </div>

          </div>

          <div className="system-status">

            {/* DASHBOARD */}

            <div className="status-row">

              <span>
                Dashboard
              </span>

              <strong className="status-online">
                <i></i>
                Online
              </strong>

            </div>

            {/* API */}

            <div className="status-row">

              <span>
                Emergency API
              </span>

              <strong
                className={
                  demoMode
                    ? "status-offline"
                    : "status-online"
                }
              >
                <i></i>

                {demoMode
                  ? "Offline"
                  : "Connected"}
              </strong>

            </div>

            {/* OPERATOR */}

            <div className="status-row">

              <span>
                Logged-in Operator
              </span>

              <strong>
                {user?.username ||
                  user?.name ||
                  "Rescuer"}
              </strong>

            </div>

            {/* INCIDENT STATUS */}

            <div className="status-row">

              <span>
                Critical Alerts
              </span>

              <strong
                className={
                  criticalCount > 0
                    ? "status-offline"
                    : "status-online"
                }
              >
                <i></i>

                {loading
                  ? "Checking..."
                  : criticalCount > 0
                  ? `${criticalCount} Active`
                  : "Clear"}
              </strong>

            </div>

          </div>

        </div>

      </section>

    </div>
  );
};

export default Dashboard;
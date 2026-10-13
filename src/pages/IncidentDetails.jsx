import { useEffect, useState } from "react";
import {
  Link,
  useLocation,
  useParams,
} from "react-router-dom";
import { apiRequest } from "../services/api";

/* =========================================
   SEVERITY CLASS
========================================= */
const getSeverityClass = (severity) => {
  switch (String(severity || "").toUpperCase()) {
    case "CRITICAL":
      return "severity-critical";

    case "HIGH":
      return "severity-high";

    case "MEDIUM":
      return "severity-medium";

    case "LOW":
      return "severity-low";

    default:
      return "severity-unknown";
  }
};

/* =========================================
   STATUS CLASS
========================================= */
const getStatusClass = (status) => {
  switch (String(status || "").toUpperCase()) {
    case "RESCUED":
    case "RESOLVED":
    case "CLOSED":
      return "status-resolved";

    case "RESCUE_IN_PROGRESS":
    case "IN_PROGRESS":
    case "ACTIVE":
      return "status-active";

    case "ASSIGNED":
    case "PENDING":
      return "status-pending";

    case "NEW":
      return "status-new";

    default:
      return "status-unknown";
  }
};

/* =========================================
   RESOURCE RECOMMENDATION
========================================= */
const getResourceRecommendation = (incident) => {
  const people = Number(incident?.people_count || 1);

  const severity = String(
    incident?.severity || ""
  ).toUpperCase();

  const disaster = String(
    incident?.disaster_type || ""
  ).toUpperCase();

  let rescuers = 2;
  let ambulances = 1;
  let medicalTeams = 1;
  let rescueVehicles = 1;

  const equipment = [];
  const supplies = [];

  /* -----------------------------------------
     BASED ON NUMBER OF PEOPLE
  ----------------------------------------- */

  if (people <= 2) {
    rescuers = 2;
    ambulances = 1;
  } else if (people <= 5) {
    rescuers = 4;
    ambulances = 1;
  } else if (people <= 10) {
    rescuers = 6;
    ambulances = 2;
  } else {
    rescuers = 8;
    ambulances = 3;
  }

  /* -----------------------------------------
     BASED ON SEVERITY
  ----------------------------------------- */

  if (severity === "CRITICAL") {
    rescuers += 2;
    ambulances += 1;
    medicalTeams += 1;
    rescueVehicles += 1;
  } else if (severity === "HIGH") {
    rescuers += 1;
  }

  /* -----------------------------------------
     FLOOD
  ----------------------------------------- */

  if (disaster.includes("FLOOD")) {
    equipment.push("Life jackets");
    equipment.push("Rescue boat");

    supplies.push("Drinking water");
    supplies.push("Emergency food");
  }

  /* -----------------------------------------
     FIRE
  ----------------------------------------- */

  if (
    disaster.includes("FIRE") ||
    disaster.includes("WILDFIRE")
  ) {
    equipment.push("Fire protection equipment");
    equipment.push("Breathing apparatus");

    rescueVehicles += 1;
  }

  /* -----------------------------------------
     EARTHQUAKE / BUILDING COLLAPSE
  ----------------------------------------- */

  if (
    disaster.includes("COLLAPSE") ||
    disaster.includes("EARTHQUAKE")
  ) {
    equipment.push("Search & rescue equipment");
    equipment.push("Cutting tools");
    equipment.push("Safety helmets");

    rescuers += 2;
  }

  /* -----------------------------------------
     ACCIDENT / CRASH
  ----------------------------------------- */

  if (
    disaster.includes("ACCIDENT") ||
    disaster.includes("CRASH")
  ) {
    equipment.push("First-aid equipment");
    equipment.push("Extrication equipment");
  }

  return {
    rescuers,
    ambulances,
    medicalTeams,
    rescueVehicles,
    equipment,
    supplies,
  };
};

/* =========================================
   RESCUE PROGRESS
========================================= */
const RescueProgress = ({ status }) => {
  const statuses = [
    {
      value: "NEW",
      label: "Reported",
    },
    {
      value: "ASSIGNED",
      label: "Assigned",
    },
    {
      value: "RESCUE_IN_PROGRESS",
      label: "Rescue In Progress",
    },
    {
      value: "RESCUED",
      label: "Rescued",
    },
  ];

  const normalizedStatus = String(
    status || "NEW"
  ).toUpperCase();

  const currentIndex = statuses.findIndex(
    (item) => item.value === normalizedStatus
  );

  return (
    <section className="rescue-progress-card">
      <div className="details-card-header">
        <div>
          <h3>Rescue Progress</h3>

          <p className="resource-subtitle">
            Current emergency response lifecycle
          </p>
        </div>
      </div>

      <div className="rescue-progress">
        {statuses.map((item, index) => {
          const completed =
            currentIndex >= 0 && index <= currentIndex;

          const current =
            currentIndex >= 0 &&
            index === currentIndex;

          return (
            <div
              key={item.value}
              className={`progress-step ${
                completed ? "completed" : ""
              } ${current ? "current" : ""}`}
            >
              <div className="progress-dot">
                {completed ? "✓" : index + 1}
              </div>

              <span>{item.label}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
};

/* =========================================
   MAIN INCIDENT DETAILS
========================================= */
const IncidentDetails = () => {
  const { id } = useParams();
  const location = useLocation();

  const initialIncident =
    location.state?.incident || null;

  const [incident, setIncident] =
    useState(initialIncident);

  const [loading, setLoading] =
    useState(!initialIncident);

  const [error, setError] =
    useState("");

  /* -----------------------------------------
     FETCH INCIDENT
  ----------------------------------------- */
useEffect(() => {
  if (initialIncident) {
    setIncident(initialIncident);
    setLoading(false);
    return;
  }

  setLoading(false);
  setError("Incident data is not available in demo mode.");
}, [initialIncident]);

  /* -----------------------------------------
     LOADING
  ----------------------------------------- */

  if (loading) {
    return (
      <div className="details-state">
        <p>Loading incident details...</p>
      </div>
    );
  }

  /* -----------------------------------------
     ERROR
  ----------------------------------------- */

  if (error) {
    return (
      <div className="details-state">
        <div className="error-message">
          {error}
        </div>

        <Link
          to="/incidents"
          className="back-link"
        >
          ← Back to Incidents
        </Link>
      </div>
    );
  }

  /* -----------------------------------------
     NOT FOUND
  ----------------------------------------- */

  if (!incident) {
    return (
      <div className="details-state">
        <h2>Incident not found</h2>

        <Link
          to="/incidents"
          className="back-link"
        >
          ← Back to Incidents
        </Link>
      </div>
    );
  }

  /* -----------------------------------------
     AI CONFIDENCE
  ----------------------------------------- */

  const aiConfidence =
    incident.ai_confidence != null
      ? `${Math.round(
          Number(incident.ai_confidence) * 100
        )}%`
      : "N/A";

  /* -----------------------------------------
     RESOURCE RECOMMENDATION
  ----------------------------------------- */

  const resources =
    getResourceRecommendation(incident);

  /* -----------------------------------------
     PAGE
  ----------------------------------------- */

  return (
    <div className="incident-details-page">

      {/* =====================================
          TOP BAR
      ====================================== */}

      <div className="details-topbar">
        <Link
          to="/incidents"
          className="back-link"
        >
          ← Back to Incidents
        </Link>
      </div>

      {/* =====================================
          INCIDENT HERO
      ====================================== */}

      <section className="incident-hero">
        <div>
          <span className="incident-label">
            EMERGENCY INCIDENT
          </span>

          <h2>
            {incident.disaster_type ||
              "Unknown Incident"}
          </h2>

          <p>
            Incident #{incident.id}
          </p>
        </div>

        <div className="incident-badges">

          <span
            className={`severity-badge ${getSeverityClass(
              incident.severity
            )}`}
          >
            {incident.severity ||
              "UNKNOWN"}
          </span>

          <span
            className={`status-badge ${getStatusClass(
              incident.status
            )}`}
          >
            {incident.status ||
              "UNKNOWN"}
          </span>

        </div>
      </section>

      {/* =====================================
          RESCUE PROGRESS
      ====================================== */}

      <RescueProgress
        status={incident.status}
      />

      {/* =====================================
          QUICK STATS
      ====================================== */}

      <section className="details-stats">

        <div className="detail-stat">
          <span>Priority Score</span>

          <strong className="priority-large">
            {incident.priority_score ??
              "N/A"}
          </strong>
        </div>

        <div className="detail-stat">
          <span>AI Confidence</span>

          <strong>
            {aiConfidence}
          </strong>
        </div>

        <div className="detail-stat">
          <span>People Affected</span>

          <strong>
            {incident.people_count ??
              "N/A"}
          </strong>
        </div>

        <div className="detail-stat">
          <span>Status</span>

          <strong>
            {incident.status ||
              "N/A"}
          </strong>
        </div>

      </section>

      {/* =====================================
          DETAILS GRID
      ====================================== */}

      <section className="details-grid">

        {/* ===================================
            AI RESOURCE RECOMMENDATION
        ==================================== */}

        <div className="details-card resource-card">

          <div className="details-card-header">

            <div>
              <h3>
                AI Resource Recommendation
              </h3>

              <p className="resource-subtitle">
                Recommended resources for this
                emergency
              </p>
            </div>

            <span className="ai-label">
              AI
            </span>

          </div>

          {/* RESOURCE NUMBERS */}

          <div className="resource-grid">

            {/* RESCUERS */}

            <div className="resource-item">

              <span className="resource-icon">
                👨‍🚒
              </span>

              <div>
                <span>
                  Rescuers
                </span>

                <strong>
                  {resources.rescuers}
                </strong>
              </div>

            </div>

            {/* AMBULANCES */}

            <div className="resource-item">

              <span className="resource-icon">
                🚑
              </span>

              <div>
                <span>
                  Ambulances
                </span>

                <strong>
                  {resources.ambulances}
                </strong>
              </div>

            </div>

            {/* MEDICAL TEAM */}

            <div className="resource-item">

              <span className="resource-icon">
                🏥
              </span>

              <div>
                <span>
                  Medical Teams
                </span>

                <strong>
                  {resources.medicalTeams}
                </strong>
              </div>

            </div>

            {/* RESCUE VEHICLES */}

            <div className="resource-item">

              <span className="resource-icon">
                🚒
              </span>

              <div>
                <span>
                  Rescue Vehicles
                </span>

                <strong>
                  {resources.rescueVehicles}
                </strong>
              </div>

            </div>

          </div>

          {/* EQUIPMENT */}

          {resources.equipment.length >
            0 && (
            <div className="resource-section">

              <h4>
                Required Equipment
              </h4>

              <div className="resource-tags">

                {resources.equipment.map(
                  (item) => (
                    <span key={item}>
                      {item}
                    </span>
                  )
                )}

              </div>

            </div>
          )}

          {/* SUPPLIES */}

          {resources.supplies.length >
            0 && (
            <div className="resource-section">

              <h4>
                Required Supplies
              </h4>

              <div className="resource-tags">

                {resources.supplies.map(
                  (item) => (
                    <span key={item}>
                      {item}
                    </span>
                  )
                )}

              </div>

            </div>
          )}

          {/* RECOMMENDATION REASON */}

          <div className="resource-reason">

            <strong>
              Recommendation Basis
            </strong>

            <p>
              Based on{" "}
              {incident.people_count ||
                1}{" "}
              affected person(s),{" "}
              {incident.severity ||
                "unknown"}{" "}
              severity, and the reported{" "}
              {incident.disaster_type ||
                "emergency"}.
            </p>

          </div>

        </div>

        {/* ===================================
            VICTIM INFORMATION
        ==================================== */}

        <div className="details-card">

          <div className="details-card-header">
            <h3>
              Victim Information
            </h3>
          </div>

          <div className="detail-list">

            <div>
              <span>Name</span>

              <strong>
                {incident.name ||
                  incident.victim_name ||
                  "Unknown"}
              </strong>
            </div>

            <div>
              <span>
                People Count
              </span>

              <strong>
                {incident.people_count ??
                  "N/A"}
              </strong>
            </div>

            <div>
              <span>
                Message
              </span>

              <strong>
                {incident.message ||
                  "No message provided."}
              </strong>
            </div>

          </div>

        </div>

        {/* ===================================
            LOCATION
        ==================================== */}

        <div className="details-card">

          <div className="details-card-header">
            <h3>
              Location
            </h3>
          </div>

          <div className="detail-list">

            <div>
              <span>
                Latitude
              </span>

              <strong>
                {incident.latitude ??
                  "N/A"}
              </strong>
            </div>

            <div>
              <span>
                Longitude
              </span>

              <strong>
                {incident.longitude ??
                  "N/A"}
              </strong>
            </div>

          </div>

          <Link
            to="/map"
            className="map-link"
          >
            View on Rescue Map →
          </Link>

        </div>

        {/* ===================================
            AI EMERGENCY ANALYSIS
        ==================================== */}

        <div className="details-card ai-card">

          <div className="details-card-header">

            <h3>
              AI Emergency Analysis
            </h3>

            <span className="ai-label">
              AI
            </span>

          </div>

          <div className="detail-list">

            <div>
              <span>
                Disaster Type
              </span>

              <strong>
                {incident.disaster_type ||
                  "N/A"}
              </strong>
            </div>

            <div>
              <span>
                Severity
              </span>

              <strong>
                {incident.severity ||
                  "N/A"}
              </strong>
            </div>

            <div>
              <span>
                Priority Score
              </span>

              <strong className="priority-large">
                {incident.priority_score ??
                  "N/A"}
              </strong>
            </div>

            <div>
              <span>
                AI Confidence
              </span>

              <strong>
                {aiConfidence}
              </strong>
            </div>

          </div>

        </div>

        {/* ===================================
            RESCUE STATUS
        ==================================== */}

        <div className="details-card">

          <div className="details-card-header">

            <h3>
              Rescue Status
            </h3>

          </div>

          <div className="status-large">

            <span
              className={`status-badge ${getStatusClass(
                incident.status
              )}`}
            >
              {incident.status ||
                "UNKNOWN"}
            </span>

          </div>

          <p className="status-help">
            Rescue status is managed by
            authorized rescue operators.
          </p>

        </div>

      </section>

    </div>
  );
};

export default IncidentDetails;
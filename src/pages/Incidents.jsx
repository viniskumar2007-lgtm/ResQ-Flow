import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
   INCIDENTS PAGE
========================================= */

const Incidents = () => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  /* =======================================
     FETCH INCIDENTS
  ======================================= */

  const fetchIncidents = async () => {
    setError("");

    try {
      const data = await apiRequest("/api/incidents");

      const incidentList = Array.isArray(data)
        ? data
        : data.incidents || [];

      setIncidents(incidentList);
    } catch (err) {
      setError(
        err.message || "Failed to load incidents."
      );
    } finally {
      setLoading(false);
    }
  };

  /* =======================================
     LOAD ON PAGE OPEN
  ======================================= */

  useEffect(() => {
    fetchIncidents();
  }, []);

  /* =======================================
     UPDATE INCIDENT STATUS
  ======================================= */

  const updateIncidentStatus = async (
    incidentId,
    newStatus
  ) => {
    try {
      setError("");

      await apiRequest(
        `/api/incidents/${incidentId}/status`,
        {
          method: "PUT",
          body: JSON.stringify({
            status: newStatus,
          }),
        }
      );

      /*
       * Update the row immediately instead of
       * waiting for another GET request.
       */
      setIncidents((currentIncidents) =>
        currentIncidents.map((incident) =>
          incident.id === incidentId
            ? {
                ...incident,
                status: newStatus,
              }
            : incident
        )
      );
    } catch (err) {
      setError(
        err.message ||
          "Failed to update incident status."
      );
    }
  };

  /* =======================================
     PAGE
  ======================================= */

  return (
    <div className="incidents-page">

      {/* ===================================
          PAGE HEADER
      ==================================== */}

      <section className="page-heading">

        <div>
          <h2>
            Emergency Incidents
          </h2>

          <p>
            Monitor and coordinate reported
            emergencies.
          </p>
        </div>

        <button
          className="refresh-button"
          onClick={fetchIncidents}
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh"}
        </button>

      </section>

      {/* ===================================
          ERROR
      ==================================== */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* ===================================
          INCIDENT PANEL
      ==================================== */}

      <section className="incidents-panel">

        <div className="incidents-panel-header">

          <div>
            <h3>
              All Incidents
            </h3>

            <span>
              {incidents.length} incident
              {incidents.length !== 1
                ? "s"
                : ""}
            </span>
          </div>

        </div>

        {/* =================================
            LOADING
        ================================== */}

        {loading ? (
          <div className="empty-state">
            <p>
              Loading incidents...
            </p>
          </div>

        ) : incidents.length === 0 ? (

          /* ===============================
             NO INCIDENTS
          ================================ */

          <div className="empty-state">

            <div className="empty-icon">
              ✓
            </div>

            <h3>
              No incidents found
            </h3>

            <p>
              There are currently no
              emergency incidents reported.
            </p>

          </div>

        ) : (

          /* ===============================
             INCIDENT TABLE
          ================================ */

          <div className="incident-table-wrapper">

            <table className="incident-table">

              <thead>
                <tr>
                  <th>Incident</th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Priority</th>
                  <th>People</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>

                {incidents.map((incident) => (

                  <tr key={incident.id}>

                    {/* INCIDENT */}

                    <td>
                      <strong>
                        #{incident.id}
                      </strong>
                    </td>

                    {/* TYPE */}

                    <td>
                      {incident.disaster_type ||
                        "Unknown"}
                    </td>

                    {/* SEVERITY */}

                    <td>
                      <span
                        className={`severity-badge ${getSeverityClass(
                          incident.severity
                        )}`}
                      >
                        {incident.severity ||
                          "UNKNOWN"}
                      </span>
                    </td>

                    {/* PRIORITY */}

                    <td>
                      <strong className="priority-score">
                        {incident.priority_score ??
                          "N/A"}
                      </strong>
                    </td>

                    {/* PEOPLE */}

                    <td>
                      {incident.people_count ??
                        "N/A"}
                    </td>

                    {/* STATUS */}

                    <td>

                      <select
                        className={`status-select ${getStatusClass(
                          incident.status
                        )}`}
                        value={
                          incident.status ||
                          "NEW"
                        }
                        onChange={(event) =>
                          updateIncidentStatus(
                            incident.id,
                            event.target.value
                          )
                        }
                      >

                        <option value="NEW">
                          New
                        </option>

                        <option value="ASSIGNED">
                          Assigned
                        </option>

                        <option value="RESCUE_IN_PROGRESS">
                          In Progress
                        </option>

                        <option value="RESCUED">
                          Rescued
                        </option>

                      </select>

                    </td>

                    {/* VIEW */}

                    <td>

                      <Link
                        to={`/incidents/${incident.id}`}
                        state={{
                          incident: incident,
                        }}
                        className="view-button"
                      >
                        View
                      </Link>

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>
        )}

      </section>

    </div>
  );
};

export default Incidents;
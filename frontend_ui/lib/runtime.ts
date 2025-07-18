import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
import { api, getAuthToken } from "./api";

// Geological runtime configuration for assistant-ui
export const useGeologicalRuntime = () => {
  return useChatRuntime({
    api: "/api/chat/geological",
    // Temporarily disable auth headers to test basic functionality
    // headers: async (): Promise<Record<string, string>> => {
    //   const token = getAuthToken();
    //   if (token) {
    //     return { Authorization: `Bearer ${token}` };
    //   }
    //   return {};
    // },
  });
};

// Custom tools for geological data exploration
export const geologicalTools = {
  // Tool to get geological site information
  getSiteInfo: {
    description: "Get detailed information about a geological site",
    parameters: {
      type: "object",
      properties: {
        siteId: {
          type: "string",
          description: "The ID of the geological site"
        }
      },
      required: ["siteId"]
    },
    execute: async ({ siteId }: { siteId: string }) => {
      try {
        const response = await api.geological.getSite(siteId);
        return {
          success: true,
          data: response.data
        };
      } catch {
        return {
          success: false,
          error: "Failed to fetch site information"
        };
      }
    }
  },

  // Tool to filter geological sites
  filterSites: {
    description: "Filter geological sites based on criteria",
    parameters: {
      type: "object",
      properties: {
        filters: {
          type: "object",
          description: "Filter criteria for geological sites"
        }
      },
      required: ["filters"]
    },
    execute: async ({ filters }: { filters: Record<string, unknown> }) => {
      try {
        const response = await api.geological.filterSites(filters);
        return {
          success: true,
          data: response.data
        };
      } catch {
        return {
          success: false,
          error: "Failed to filter sites"
        };
      }
    }
  },

  // Tool to get site geometry
  getSiteGeometry: {
    description: "Get geometric data for a geological site",
    parameters: {
      type: "object",
      properties: {
        siteId: {
          type: "string",
          description: "The ID of the geological site"
        }
      },
      required: ["siteId"]
    },
    execute: async ({ siteId }: { siteId: string }) => {
      try {
        const response = await api.geological.getSiteGeometry(siteId);
        return {
          success: true,
          data: response.data
        };
      } catch {
        return {
          success: false,
          error: "Failed to fetch site geometry"
        };
      }
    }
  }
};

// Runtime configuration with tools
export const useGeologicalRuntimeWithTools = () => {
  return useChatRuntime({
    api: "/api/chat/geological-tools",
  });
}; 
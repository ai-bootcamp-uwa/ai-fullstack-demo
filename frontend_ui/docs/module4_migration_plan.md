# Module 4 Migration Plan: Unified Map + Chat UI

## Goal

Incrementally migrate from separate chat/map pages to a unified `/explore` route with a Google Maps-like interface, minimizing code changes at each step and verifying functionality after every update.

---

## Step-by-Step Plan

| Step | Description                                                                     | Success Criteria                                     | Rollback Plan                        |
| ---- | ------------------------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------ |
| 1    | **Create `/explore` route** (copy existing map or chat page as placeholder)     | `/explore` loads and displays map or chat, no errors | Delete new route, revert to old      |
| 2    | **Add GeologicalExplorer layout** (split screen: sidebar + map, static content) | Layout renders, no errors                            | Revert new component, keep old route |
| 3    | **Move map into GeologicalExplorer**                                            | Map renders in new layout                            | Move map back to old page            |
| 4    | **Move chat into sidebar**                                                      | Chat renders in sidebar                              | Move chat back to old page           |
| 5    | **Sidebar collapse/expand**                                                     | Sidebar can be collapsed/expanded                    | Remove collapse logic                |
| 6    | **Connect map marker click to sidebar context**                                 | Clicking marker updates sidebar context              | Remove context logic                 |
| 7    | **Add clustering and custom icons**                                             | Markers cluster, icons show                          | Remove clustering/icons              |
| 8    | **Add layer controls and geological tiles**                                     | User can switch map layers                           | Remove layer controls                |
| 9    | **Mobile responsiveness**                                                       | Layout adapts to small screens                       | Remove responsive CSS                |

---

## Testing After Each Step

- Run the app and visit `/explore`
- Confirm new feature works and nothing else is broken
- Commit changes if successful

---

## Guiding Principles

- **Minimal change per step**
- **Test after each step**
- **Easy rollback if needed**
- **No disruption to existing routes until migration is complete**

---

## Next Step

**Step 1:**

- Create `/explore` route as a copy of your current map or chat page.
- Test: `/explore` loads and displays content.

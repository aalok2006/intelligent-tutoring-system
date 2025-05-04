from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.learning_path_service import LearningPathService
from ..services.content_service import ContentService # To get content details for visualization

learning_path_bp = Blueprint('learning_path', __name__, url_prefix='/api/path')

@learning_path_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_path():
    user_id = get_jwt_identity()
    path_service = LearningPathService()
    content_service = ContentService() # Need content service

    user_path = path_service.get_active_path(user_id)

    if not user_path:
        # If no path exists, trigger initial generation (simple trigger for testing, real flow is after diagnostic)
        # This allows testing QA-FR1.1 manually after user registration if diagnostic is skipped initially
        # In Phase 1, we might trigger PE directly here for testing, but later this should be rare.
        # print(f"No active path found for user {user_id}. Attempting basic generation.")
        # from ..services.personalization_engine import PersonalizationEngine
        # pe = PersonalizationEngine()
        # user_path = pe.generate_initial_path(user_id) # This needs diagnostic results ideally!

        # For now, just return empty/not found if no path is there
        return jsonify({'message': 'No active learning path found.'}), 404


    # --- Prepare data for visualization (FR1.5) ---
    path_nodes_data = []
    # Fetch all nodes for the path
    all_nodes = path_service.get_path_nodes(user_path.id)

    # Fetch content details for each node
    # This can be optimized with a single query if relationships are set up,
    # or fetching content items in bulk.
    node_details = {}
    content_ids = [node.content_item_id for node in all_nodes]
    content_items = content_service.get_content_by_ids(content_ids) # Assume this method exists
    for item in content_items:
        node_details[item.id] = item


    for node in all_nodes:
        content_item = node_details.get(node.content_item_id)
        node_data = {
            'id': node.id,
            'content_item_id': node.content_item_id,
            'node_type': node.node_type,
            'status': node.status,
            'order': node.order_in_path,
            'title': content_item.title if content_item else 'Unknown Content',
            'type': content_item.type if content_item else 'unknown',
            # Add other data needed for visualization (e.g., parent_node_id for branches)
            'parent_node_id': node.parent_node_id # Needed for visualization connections
        }
        path_nodes_data.append(node_data)

    # Simple representation of connections for visualization
    # This needs refinement depending on how the frontend visualizes
    connections = []
    # For a simple linear path, connections are just (node_order, node_order+1)
    # For branched paths (remedial), you need to use parent_node_id
    for node in all_nodes:
        if node.parent_node_id:
             connections.append({
                 'from_node_id': node.parent_node_id,
                 'to_node_id': node.id,
                 'type': node.node_type # e.g., 'remedial_branch'
             })
        # Add connections for linear sequence if not a branch start
        is_branch_start = any(n.parent_node_id == node.id for n in all_nodes)
        if node.status != 'completed' and not is_branch_start: # Simple logic: next node is after current if not a branch start
             next_node = next((n for n in all_nodes if n.order_in_path == node.order_in_path + 1 and n.parent_node_id is None), None)
             if next_node:
                  connections.append({
                     'from_node_id': node.id,
                     'to_node_id': next_node.id,
                     'type': 'sequence'
                  })


    path_representation = {
        'path_id': user_path.id,
        'current_node_id': user_path.current_node_id,
        'nodes': path_nodes_data,
        'connections': connections # Data structure depends on frontend visualization library
    }


    return jsonify(path_representation), 200

# Add endpoint to mark a node as complete (triggered by assessment service)
# @learning_path_bp.route('/node/<int:node_id>/complete', methods=['POST'])
# @jwt_required()
# def complete_node(node_id):
#     user_id = get_jwt_identity()
#     path_service = LearningPathService()
#     # In real implementation, this should be called by AssessmentService
#     # *after* a user successfully completes the content/assessment associated with the node.
#     # This endpoint is simplified for direct testing if needed.
#     success = path_service.mark_node_complete(user_id, node_id) # Service method needed
#     if success:
#          # Trigger PE for adaptation based on performance on this node
#          # from ..services.personalization_engine import PersonalizationEngine
#          # pe = PersonalizationEngine()
#          # pe.adapt_path_after_node_completion.delay(user_id, node_id) # Needs performance data!
#          return jsonify({'message': f'Node {node_id} marked complete.'}), 200
#     return jsonify({'message': 'Node not found or not current node.'}), 400

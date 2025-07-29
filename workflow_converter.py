"""
Workflow Converter for ComfyUI Server
Converts ComfyUI workflow JSON to API format without requiring frontend
"""

import json
from typing import Dict, Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

def workflow_json_to_api(workflow_json: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Converts a ComfyUI workflow JSON directly to API format
    without needing to implement a full graph structure.
    
    Args:
        workflow_json: The workflow JSON data
        options: Configuration options (queueNodeIds, etc.)
    
    Returns:
        The API format workflow
    """
    if options is None:
        options = {}
    
    queue_node_ids = options.get('queueNodeIds', [])
    
    # Create a map of links for easy lookup
    link_map = {}
    if workflow_json.get('links'):
        for link in workflow_json['links']:
            if len(link) >= 6:
                link_map[link[0]] = {
                    'origin_id': link[1],
                    'origin_slot': link[2],
                    'target_id': link[3],
                    'target_slot': link[4],
                    'type': link[5]
                }
    
    # Create a map of nodes for easy lookup
    node_map = {}
    for node in workflow_json.get('nodes', []):
        node_map[node['id']] = node
    
    output = {}
    
    # Process each node
    for node in workflow_json.get('nodes', []):
        # Skip nodes that are muted or bypassed
        if node.get('mode') in [0, 1, 4]:  # NEVER, BYPASS, or alternative BYPASS
            continue
        
        inputs = {}
        
        # Process widgets_values from the node
        if node.get('widgets_values') and isinstance(node['widgets_values'], list):
            # Create a map of widget names to values
            widget_values_map = {}
            
            # Process widgets if they exist in the node
            if node.get('inputs') and isinstance(node['inputs'], list):
                for i, input_slot in enumerate(node['inputs']):
                    if isinstance(input_slot, dict) and input_slot.get('widget') and input_slot['widget'].get('name'):
                        # This is a widget input, get its value from widgets_values
                        if i < len(node['widgets_values']) and node['widgets_values'][i] is not None:
                            widget_values_map[input_slot['widget']['name']] = node['widgets_values'][i]
            
            # Add all widget values to inputs
            for widget_name, widget_value in widget_values_map.items():
                # By default, Array values are reserved to represent node connections.
                # We need to wrap the array as an object to avoid the misinterpretation
                # of the array as a node connection.
                if isinstance(widget_value, list):
                    inputs[widget_name] = {'__value__': widget_value}
                else:
                    inputs[widget_name] = widget_value
        
        # Process node connections from the node
        if node.get('inputs') and isinstance(node['inputs'], list):
            for input_slot in node['inputs']:
                if isinstance(input_slot, dict) and input_slot.get('name'):
                    link_id = input_slot.get('link')
                    
                    if link_id and link_id in link_map:
                        link = link_map[link_id]
                        inputs[input_slot['name']] = [
                            str(link['origin_id']),
                            link['origin_slot']
                        ]
        
        # Add the node to output
        output[str(node['id'])] = {
            'inputs': inputs,
            # Use the node's class_type or fallback to type
            'class_type': node.get('class_type') or node.get('type') or 'Unknown',
            # Ignored by the backend.
            '_meta': {
                'title': node.get('title') or node.get('properties', {}).get('Node name for S&R') or 'Unknown'
            }
        }
    
    # Remove inputs connected to removed nodes
    for node_data in output.values():
        inputs_to_remove = []
        for input_name, input_value in node_data['inputs'].items():
            if isinstance(input_value, list) and len(input_value) == 2 and input_value[0] not in output:
                inputs_to_remove.append(input_name)
        
        for input_name in inputs_to_remove:
            del node_data['inputs'][input_name]
    
    # Partial execution - only include specified nodes and their dependencies
    if queue_node_ids:
        new_output = {}
        processed_nodes = set()
        
        def add_node_and_dependencies(node_id):
            node_id_str = str(node_id)
            if node_id_str in processed_nodes:
                return
            
            if node_id_str not in output:
                return
            
            processed_nodes.add(node_id_str)
            new_output[node_id_str] = output[node_id_str]
            
            # Add dependencies
            for input_value in new_output[node_id_str]['inputs'].values():
                if isinstance(input_value, list) and len(input_value) == 2:
                    add_node_and_dependencies(input_value[0])
        
        for node_id in queue_node_ids:
            add_node_and_dependencies(node_id)
        
        return new_output
    
    return output

def validate_workflow_json(workflow_json: Dict[str, Any]) -> bool:
    """
    Validates that the workflow JSON has the required structure.
    
    Args:
        workflow_json: The workflow JSON to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(workflow_json, dict):
        return False
    
    if 'nodes' not in workflow_json or not isinstance(workflow_json['nodes'], list):
        return False
    
    if 'version' not in workflow_json:
        return False
    
    return True

def convert_workflow_to_api(workflow_data: Union[str, Dict[str, Any]], options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main function to convert workflow data to API format.
    
    Args:
        workflow_data: Either a JSON string or a dictionary containing the workflow
        options: Optional configuration options
    
    Returns:
        Dictionary with the converted API format workflow
    
    Raises:
        ValueError: If the workflow data is invalid
    """
    if options is None:
        options = {}
    
    # Parse JSON if it's a string
    if isinstance(workflow_data, str):
        try:
            workflow_json = json.loads(workflow_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in workflow data: {e}")
    else:
        workflow_json = workflow_data
    
    # Validate the workflow structure
    if not validate_workflow_json(workflow_json):
        raise ValueError("Invalid workflow structure")
    
    # Convert to API format
    try:
        api_workflow = workflow_json_to_api(workflow_json, options)
        return api_workflow
    except Exception as e:
        logger.error(f"Error converting workflow to API format: {e}")
        raise ValueError(f"Failed to convert workflow: {e}") 
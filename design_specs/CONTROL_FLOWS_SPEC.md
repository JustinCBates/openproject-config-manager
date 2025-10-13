# Control Flow Specification - Config Manager

> **Design-first specification for iterative development**  
> Use this to communicate flow changes before implementation exists

## Entry Points
```yaml
cli:
  status: IMPLEMENTED
  description: "Main CLI entry point"
  calls: [configure, update, validate, discover, export, version]
  
configure:
  status: IMPLEMENTED  
  description: "Run complete configuration process"
  flow_id: "main_config_flow"
```

## Flow Implementations
```yaml
main_config_flow:
  description: "Primary Configuration Process"
  phases:
    - phase_id: "discovery"
      name: "Discovery Phase"
      status: IMPLEMENTED
      description: "Discover system environment and generate intelligent defaults"
      sub_flows: ["discovery_flow"]
      artifacts_produced: ["discovery_data", "enhanced_defaults_file"]
      artifacts_consumed: []
      
    - phase_id: "tui_mapping"
      name: "TUI Defaults Mapping"
      status: IMPLEMENTED
      description: "Transform rich enhanced defaults to simple TUI format"
      artifacts_produced: ["tui_defaults_file"]
      artifacts_consumed: ["enhanced_defaults_file"]
      
    - phase_id: "collection"
      name: "Interactive Collection"
      status: IMPLEMENTED
      description: "Collect user configuration via interactive UI"
      artifacts_produced: ["user_configuration"]
      artifacts_consumed: ["tui_defaults_file"]
      
    - phase_id: "validation"
      name: "Validation Phase"
      status: IMPLEMENTED
      description: "Validate collected configuration"
      artifacts_produced: ["validated_configuration", "validation_report"]
      artifacts_consumed: ["user_configuration", "discovery_data"]
      decision_point: "continue_on_validation_failure"
      
    - phase_id: "export"
      name: "Export Phase"
      status: IMPLEMENTED
      description: "Export configuration for deployment"
      artifacts_produced: ["deployment_artifacts"]
      artifacts_consumed: ["validated_configuration", "discovery_data"]
      
  planned_insertions:
    - insert_after: "collection"
      phase_id: "pre_validation_cleanup"
      name: "Pre-validation Cleanup"
      status: PLANNED
      description: "Clean up configuration before validation"
      artifacts_produced: ["sanitized_configuration"]
      artifacts_consumed: ["user_configuration"]
      
    - insert_before: "export"
      phase_id: "final_review"
      name: "Final Review"
      status: PLANNED
      description: "Show summary for user approval before export"
      artifacts_produced: ["approval_confirmation"]
      artifacts_consumed: ["validated_configuration", "validation_report"]

discovery_flow:
  description: "System Discovery and Intelligent Defaults Generation"
  steps:
    - step_id: "env_discovery"
      name: "Environment Variables"
      status: IMPLEMENTED
      description: "Discover relevant environment variables"
      artifacts_produced: ["environment_data"]
      
    - step_id: "system_discovery"
      name: "System Information"
      status: IMPLEMENTED
      description: "Detect system resources and platform"
      artifacts_produced: ["system_data"]
      
    - step_id: "docker_discovery"
      name: "Docker Environment"
      status: IMPLEMENTED
      description: "Discover Docker containers and networks"
      artifacts_produced: ["docker_data"]
      
    - step_id: "network_discovery"
      name: "Network Discovery"
      status: IMPLEMENTED
      description: "Discover network topology and conflicts"
      artifacts_produced: ["network_data"]
      
    - step_id: "defaults_enhancement"
      name: "Enhanced Defaults Generation"
      status: IMPLEMENTED
      description: "Generate intelligent defaults from discovery data"
      artifacts_produced: ["enhanced_defaults_file"]
      artifacts_consumed: ["environment_data", "system_data", "docker_data", "network_data"]
```

## Artifacts
```yaml
# Artifacts produced and consumed throughout the configuration process
# Note: concrete_product indicates the decided filepath, implementation_status indicates if actually implemented

discovery_data:
  description: "Complete system discovery information"
  components: ["environment_data", "system_data", "docker_data", "network_data"]
  producers: ["run_discovery_phase"]
  consumers: ["run_validation_phase", "run_export_phase"]
  lifecycle: "session_scoped"
  implementation_status: "implemented"
  storage_type: "in-memory"

enhanced_defaults_file:
  description: "Rich discovery-based defaults with metadata and reasoning"
  format: "YAML file with probe sources, confidence levels, and system analysis"
  producers: ["run_discovery_phase"]
  consumers: ["tui_mapping_phase"]
  lifecycle: "persistent"
  concrete_product: "output/discovery/enhanced_defaults.yml"
  implementation_status: "planned"
  storage_type: "file"

tui_defaults_file:
  description: "Flattened defaults for TUI form engine consumption"
  format: "Simple YAML structure matching TUI field expectations"
  producers: ["tui_mapping_phase"]
  consumers: ["run_interactive_collection_phase"]
  lifecycle: "persistent"
  concrete_product: "src/openproject_config_manager/collector/layouts/defaults/config_tui.defaults.yml"
  implementation_status: "planned"
  storage_type: "file"
  
user_configuration:
  description: "User-provided configuration values"
  source: "interactive_collection"
  producers: ["run_interactive_collection_phase"]
  consumers: ["run_validation_phase", "run_export_phase"]
  lifecycle: "session_scoped"
  implementation_status: "implemented"
  storage_type: "in-memory"
  
validated_configuration:
  description: "User configuration after validation"
  source: "validation"
  producers: ["run_validation_phase"]
  consumers: ["run_export_phase"]
  lifecycle: "session_scoped"
  implementation_status: "implemented"
  storage_type: "in-memory"
  
validation_report:
  description: "Validation results and warnings"
  source: "validation"
  producers: ["run_validation_phase"]
  consumers: ["final_review", "run_export_phase"]
  lifecycle: "session_scoped"
  implementation_status: "implemented"
  storage_type: "in-memory"
  
deployment_artifacts:
  description: "Final configuration ready for deployment"
  components: ["config_file", "deployment_metadata"]
  producers: ["run_export_phase"]
  consumers: ["deploy_manager"]
  lifecycle: "persistent"
  concrete_product: "openproject.cfg (output path determined by user/CLI args)"
  implementation_status: "implemented"
  storage_type: "file"
```

## Decision Points
```yaml
continue_on_validation_failure:
  type: "user_confirmation"
  prompt: "Validation failed. Continue anyway?"
  default: false
  implemented: true
  
use_custom_output_path:
  type: "parameter_check"
  condition: "output parameter provided"
  implemented: true

confirm_destructive_changes:
  type: "user_confirmation"
  prompt: "This will overwrite existing configuration. Continue?"
  default: false
  implemented: false
  insert_before_step: "export.write_file"
```

## Artifact Flow Summary
```yaml
# Visual representation of artifact flow through the system

flow_progression:
  discovery → enhanced_defaults → collection → user_configuration → validation → validated_configuration → export → deployment_artifacts

artifact_dependencies:
  enhanced_defaults: 
    inputs: [environment_data, system_data, docker_data, network_data]
    outputs: [enhanced_defaults_file]
    
  user_configuration:
    inputs: [enhanced_defaults]
    outputs: [user_selections, user_preferences]
    
  validated_configuration:
    inputs: [user_configuration, discovery_data]
    outputs: [validated_config, validation_report]
    
  deployment_artifacts:
    inputs: [validated_configuration, discovery_data]
    outputs: [config_file, deployment_metadata]

unconsummed_artifacts:
  # Artifacts produced but not consumed by subsequent phases
  environment_data: "Available for external analysis"
  system_data: "Available for external analysis" 
  docker_data: "Available for external analysis"
  network_data: "Available for external analysis"
  validation_report: "Available for logging and audit"
```
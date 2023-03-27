import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonDef = cmdDefs.addButtonDefinition('Gears3000', 'Gears3000', 'Create Gears based on connected sketch circles', './resources')

        # Connect to the command created event.
        commandCreatedEvent = buttonDef.commandCreated
        commandCreatedEvent.add(onCommandCreated)

        # Execute the command definition.
        buttonDef.execute()

        # Keep the script running.
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def onCommandCreated(args):
    try:
        command = args.command
        inputs = command.commandInputs

        # Create a selection input.
        circleSelection = inputs.addSelectionInput('circleSelection', 'Select Circles', 'Select the sketch circles to create gears')
        circleSelection.setSelectionLimits(1)

        # Connect to the execute event.
        command.execute.add(onExecute)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def onExecute(args):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Get the input values.
        circleSelection = args.command.commandInputs.itemById('circleSelection')
        selectedCircles = circleSelection.selection(0)

        # Create gears based on the selected circles.
        createGears(selectedCircles)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createGears(selectedCircles):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Create a new component for the gears.
        rootComp = design.rootComponent
        gearComp = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        gearComp.name = "Gears3000"

        # Create the gears based on the selected circles.
        for circle in selectedCircles:
            # Create a new sketch on the circle's plane.
            sketch = gearComp.sketches.add(circle.geometry.plane)

            # Project the circle onto the sketch.
            sketch.project(circle)

            # Create the gear based on the projected circle.
            createGear(sketch, circle)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createGear(sketch, circle):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Create the gear profile.
        gearProfile = sketch.profiles.item(0)

        # Create an extrude feature for the gear.
        extrudes = design.rootComponent.features.extrudeFeatures
        gearExtrude = extrudes.addSimple(gearProfile, adsk.core.ValueInput.createByReal(1), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Rename the gear body.
        gearExtrude.bodies.item(0).name = "Gear"
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


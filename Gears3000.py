
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

        # Create a checkbox input for helical gears.
        helicalCheckbox = inputs.addBoolValueInput('helicalCheckbox', 'Helical Gears', True)

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
        helicalCheckbox = args.command.commandInputs.itemById('helicalCheckbox')
        isHelical = helicalCheckbox.value

        # Create gears based on the selected circles.
        createGears(selectedCircles, isHelical)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createGears(selectedCircles, isHelical):
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
            createGear(sketch, circle, isHelical)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createGear(sketch, circle, isHelical):
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

        # Create helical gear if requested.
        if isHelical:
            createHelicalGear(gearExtrude)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createHelicalGear(gearExtrude):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Create a coil feature for the helical gear.
        coils = design.rootComponent.features.coilFeatures
        coilInput = coils.createInput(gearExtrude.bodies.item(0), adsk.fusion.CoilFeatureOperations.CutFeatureOperation)

        # Set the coil parameters.
        coilInput.height = adsk.core.ValueInput.createByReal(1)
        coilInput.diameter = adsk.core.ValueInput.createByReal(1)
        coilInput.pitch = adsk.core.ValueInput.createByReal(0.1)
        coilInput.isClockwise = True
        coilInput.isSolid = False

        # Create the helical gear.
        helicalGear = coils.add(coilInput)

        # Rename the helical gear body.
        helicalGear.bodies.item(0).name = "Helical Gear"
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


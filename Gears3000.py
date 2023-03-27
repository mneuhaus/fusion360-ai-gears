
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

        # Create a checkbox input for bevel gears.
        bevelCheckbox = inputs.addBoolValueInput('bevelCheckbox', 'Bevel Gears', False)

        # Create inputs for new options.
        thicknessInput = inputs.addValueInput('thickness', 'Thickness', 'mm', adsk.core.ValueInput.createByReal(1))
        holeDiameterInput = inputs.addValueInput('holeDiameter', 'Hole Diameter', 'mm', adsk.core.ValueInput.createByReal(1))
        backlashInput = inputs.addValueInput('backlash', 'Backlash', 'mm', adsk.core.ValueInput.createByReal(0.1))
        pressureAngleInput = inputs.addValueInput('pressureAngle', 'Pressure Angle', 'deg', adsk.core.ValueInput.createByReal(20))
        moduleInput = inputs.addValueInput('module', 'Module', 'mm', adsk.core.ValueInput.createByReal(1))

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
        bevelCheckbox = args.command.commandInputs.itemById('bevelCheckbox')
        isBevel = bevelCheckbox.value

        # Get the new option values.
        thickness = args.command.commandInputs.itemById('thickness').value
        holeDiameter = args.command.commandInputs.itemById('holeDiameter').value
        backlash = args.command.commandInputs.itemById('backlash').value
        pressureAngle = args.command.commandInputs.itemById('pressureAngle').value
        module = args.command.commandInputs.itemById('module').value

        # Create gears based on the selected circles.
        createGears(selectedCircles, isHelical, isBevel, thickness, holeDiameter, backlash, pressureAngle, module)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createGears(selectedCircles, isHelical, isBevel, thickness, holeDiameter, backlash, pressureAngle, module):
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
            createGear(sketch, circle, isHelical, isBevel, thickness, holeDiameter, backlash, pressureAngle, module)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createGear(sketch, circle, isHelical, isBevel, thickness, holeDiameter, backlash, pressureAngle, module):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Create the gear profile.
        gearProfile = sketch.profiles.item(0)

        # Create an extrude feature for the gear.
        extrudes = design.rootComponent.features.extrudeFeatures
        gearExtrude = extrudes.addSimple(gearProfile, adsk.core.ValueInput.createByReal(thickness), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Rename the gear body.
        gearExtrude.bodies.item(0).name = "Gear"

        # Create helical gear if requested.
        if isHelical:
            createHelicalGear(gearExtrude, thickness, holeDiameter, backlash, pressureAngle, module)

        # Create bevel gear if requested.
        if isBevel:
            createBevelGear(gearExtrude, thickness, holeDiameter, backlash, pressureAngle, module)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createHelicalGear(gearExtrude, thickness, holeDiameter, backlash, pressureAngle, module):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Create a coil feature for the helical gear.
        coils = design.rootComponent.features.coilFeatures
        coilInput = coils.createInput(gearExtrude.bodies.item(0), adsk.fusion.CoilFeatureOperations.CutFeatureOperation)

        # Set the coil parameters.
        coilInput.height = adsk.core.ValueInput.createByReal(thickness)
        coilInput.diameter = adsk.core.ValueInput.createByReal(holeDiameter)
        coilInput.pitch = adsk.core.ValueInput.createByReal(backlash)
        coilInput.isClockwise = True
        coilInput.isSolid = False

        # Create the helical gear.
        helicalGear = coils.add(coilInput)

        # Rename the helical gear body.
        helicalGear.bodies.item(0).name = "Helical Gear"
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createBevelGear(gearExtrude, thickness, holeDiameter, backlash, pressureAngle, module):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Create a draft feature for the bevel gear.
        drafts = design.rootComponent.features.draftFeatures
        draftInput = drafts.createInput(gearExtrude.bodies.item(0), adsk.core.ValueInput.createByReal(pressureAngle))

        # Set the draft parameters.
        draftInput.isTangentChain = True

        # Create the bevel gear.
        bevelGear = drafts.add(draftInput)

        # Rename the bevel gear body.
        bevelGear.bodies.item(0).name = "Bevel Gear"
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


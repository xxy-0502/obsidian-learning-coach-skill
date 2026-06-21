# Concept Completion Gate

Run this gate before reporting that a lesson is finished.

1. List every reusable concept named in `本课概念`, `基础概念补齐`, and stable `[[双链]]` links.
2. For each concept, check `notes/[topic]/concepts/[concept].md`.
3. If the file is missing, empty, or contains only headings/backlinks/one-line definitions, write the full concept note.
4. A full concept note must include: definition, problem solved, why it matters, core explanation, example, common confusion or boundary condition, active recall, relationship notes, and source/provenance.
5. For STEM concepts, include definitions, assumptions/conditions, variables or units when relevant, mechanism/formula/algorithm when relevant, boundary conditions, common mistakes, and a worked or tiny example.
6. Run `python scripts/validate_concepts.py --vault LearningVault --topic "[topic]" --lesson "[lesson path]"`.
7. If the script prints `STOP: Concept completion gate failed.`, do not report the lesson as complete. Fix the listed concept files and rerun the gate.
8. Then run `python scripts/run_learning_eval.py --vault LearningVault --topic "[topic]" --lesson "[lesson path]" --result "[掌握度]"`. If the decision is not `continue`, do not advance to the next lesson.
